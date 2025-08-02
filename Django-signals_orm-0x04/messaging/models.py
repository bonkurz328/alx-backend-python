from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')    

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    def get_thread(self):
        """
        Recursively fetch all replies in the thread, optimized with prefetch_related.
        """
        return Message.objects.filter(id=self.id).prefetch_related('replies').first()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_edits')

    class Meta:
        ordering = ['-edited_at']
    
    def __str__(self):
        return f"Edit history for message {self.message.id} at {self.edited_at}"

