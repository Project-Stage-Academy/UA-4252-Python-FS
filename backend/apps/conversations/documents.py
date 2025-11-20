import uuid

from django.db import models
from django_mongodb_backend.fields import ArrayField
from django_mongodb_backend.managers import MongoManager


class Conversation(models.Model):
    conversation_id = models.UUIDField(default=uuid.uuid4, editable=False)
    participants = ArrayField(base_field=models.UUIDField(), max_size=2)
    project_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    objects = MongoManager()

    class Meta:
        db_table = "conversations"
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

        indexes = [
            models.Index(fields=["participants", "last_message_at"]),
        ]


class Message(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"

    conversation_id = models.UUIDField(editable=False)
    sender_id = models.UUIDField(editable=False)
    body = models.TextField()
    status = models.CharField(
        choices=Status.choices,
        default=Status.SENT,
        max_length=20,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MongoManager()

    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"

        indexes = [
            models.Index(fields=["conversation_id", "created_at"]),
        ]
