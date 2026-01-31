"""
Models for the AI chat agent.

Stores conversation history and messages for context continuity.
"""
import uuid

from django.db import models


class Conversation(models.Model):
    """A chat conversation with a customer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
        help_text='Session key of the user who started this conversation'
    )
    cart = models.ForeignKey(
        'orders.Cart',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='conversations',
        help_text='Associated shopping cart for this conversation'
    )
    # Store the wall analysis ID if user uploaded a room photo
    wall_analysis_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of wall analysis if room photo was uploaded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Message(models.Model):
    """A single message in a conversation."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('tool', 'Tool Result'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    # For user messages with images (room photos)
    image_url = models.URLField(blank=True, help_text='URL of attached image')
    # For assistant messages that use tools
    tool_calls = models.JSONField(
        null=True,
        blank=True,
        help_text='Tool calls made by the assistant'
    )
    tool_call_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of the tool call this message responds to'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {content_preview}"
