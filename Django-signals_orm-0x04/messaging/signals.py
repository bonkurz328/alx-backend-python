from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user
from django.contrib.auth.models import User

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
        )
        
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Check if this is an update (not a create)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Get the current user (assuming authentication middleware is set up)
                current_user = get_user(None)  # None as request is not directly available
                if not current_user.is_authenticated:
                    # Fallback to sender if no user context is available
                    current_user = instance.sender
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    editor=current_user
                )
                instance.edited = True
        except Message.DoesNotExist:
            pass  # Handle case where message doesn't exist yet

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Delete related messages (both sent and received)
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    # Delete related notifications
    Notification.objects.filter(user=instance).delete()
    # Delete related message histories
    MessageHistory.objects.filter(editor=instance).delete()


