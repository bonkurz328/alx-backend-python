from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        HOST = 'host', _('Host')
        ADMIN = 'admin', _('Admin')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    first_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        null=False,
        blank=False
    )
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Remove username field as we'll use email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        participant_names = ", ".join(
            [str(user) for user in self.participants.all()]
        )
        return f"Conversation {self.id} with {participant_names}"

class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField(
        null=False,
        blank=False
    )
    sent_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message {self.id} from {self.sender} at {self.sent_at}"

    def get_short_body(self):
        """Return shortened version of message body for display."""
        return (self.message_body[:50] + '...') if len(self.message_body) > 50 else self.message_body
    
