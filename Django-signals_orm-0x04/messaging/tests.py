from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.utils import timezone
from django.core.cache import cache

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass123')
        self.receiver = User.objects.create_user(username='receiver', password='testpass123')
        cache.clear()  # Clear cache before each test

    def test_message_creation_triggers_notification(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
            timestamp=timezone.now()
        )

        # Check if notification was created
        notification = Notification.objects.filter(user=self.receiver, message=message).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
            timestamp=timezone.now()
        )

        # Count initial notifications
        initial_count = Notification.objects.count()

        # Update message
        message.content = "Updated message"
        message.save()

        # Check that no new notification was created
        self.assertEqual(Notification.objects.count(), initial_count)

    def test_message_edit_creates_history(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message",
            timestamp=timezone.now()
        )

        # Update message content
        original_content = message.content
        message.content = "Updated message"
        message.save()

        # Check if history was created
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, original_content)
        self.assertEqual(history.message, message)
        self.assertTrue(message.edited)

    def test_no_history_on_no_content_change(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
            timestamp=timezone.now()
        )

        # Update message without changing content
        message.is_read = True
        message.save()

        # Check that no history was created
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(message.edited)

    def test_user_deletion_cleans_related_data(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
            timestamp=timezone.now()
        )

        # Create a message history
        message.content = "Updated message"
        message.save()

        # Verify initial data
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(MessageHistory.objects.count(), 1)

        # Delete the sender
        self.sender.delete()

        # Verify all related data is deleted
        self.assertEqual(Message.objects.filter(sender=self.sender).count(), 0)
        self.assertEqual(Message.objects.filter(receiver=self.sender).count(), 0)
        self.assertEqual(Notification.objects.filter(user=self.sender).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(editor=self.sender).count(), 0)

    def test_threaded_messages(self):
        # Create a parent message
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message",
            timestamp=timezone.now()
        )

        # Create a reply
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply to parent",
            parent_message=parent_message,
            timestamp=timezone.now()
        )

        # Create a nested reply
        nested_reply = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Reply to reply",
            parent_message=reply,
            timestamp=timezone.now()
        )

        # Fetch thread with optimization
        thread = parent_message.get_thread()

        # Verify the thread structure
        self.assertEqual(thread.id, parent_message.id)
        self.assertEqual(thread.replies.count(), 1)
        self.assertEqual(thread.replies.first().id, reply.id)
        self.assertEqual(thread.replies.first().replies.count(), 1)
        self.assertEqual(thread.replies.first().replies.first().id, nested_reply.id)

    def test_query_optimization(self):
        # Create a parent message and replies
        parent_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message",
            timestamp=timezone.now()
        )
        Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply",
            parent_message=parent_message,
            timestamp=timezone.now()
        )

        # Test optimized query
        with self.assertNumQueries(2):  # One for message, one for replies
            message = Message.objects.select_related('sender', 'receiver').prefetch_related('replies').get(id=parent_message.id)
            sender_username = message.sender.username
            receiver_username = message.receiver.username
            replies = list(message.replies.all())

    def test_unread_messages_manager(self):
        # Create an unread message
        unread_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            timestamp=timezone.now(),
            is_read=False
        )

        # Create a read message
        read_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Read message",
            timestamp=timezone.now(),
            is_read=True
        )

        # Test the unread manager
        unread_messages = Message.unread.unread_for_user(self.receiver)
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first().id, unread_message.id)

        # Test query optimization with .only()
        with self.assertNumQueries(1):  # Single query for unread messages
            messages = Message.unread.unread_for_user(self.receiver)
            for msg in messages:
                _ = msg.id, msg.sender.username, msg.content, msg.timestamp, msg.parent_message_id

    def test_inbox_view_caching(self):
        # Create an unread message
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            timestamp=timezone.now(),
            is_read=False
        )

        # First request to cache the view
        self.client.login(username='receiver', password='testpass123')
        with self.assertNumQueries(1):  # Expect query for initial fetch
            response = self.client.get(reverse('inbox'))
            self.assertEqual(response.status_code, 200)

        # Second request should hit cache
        with self.assertNumQueries(0):  # No queries due to cache
            response = self.client.get(reverse('inbox'))
            self.assertEqual(response.status_code, 200)

        # Create a new message and clear cache to simulate timeout
        cache.clear()
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="New unread message",
            timestamp=timezone.now(),
            is_read=False
        )

        # Request after cache clear should hit database again
        with self.assertNumQueries(1):  # Expect query after cache clear
            response = self.client.get(reverse('inbox'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "New unread message")


