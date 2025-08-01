from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.utils import timezone

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass123')
        self.receiver = User.objects.create_user(username='receiver', password='testpass123')
    
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
