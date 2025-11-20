from django.contrib import admin
from .documents import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["conversation_id", "last_message_at", "created_at"]
    list_filter = ["project_id", "created_at"]
    search_fields = ["conversation_id", "participants", "project_id"]
    readonly_fields = [
        "conversation_id",
        "participants",
        "created_at",
        "last_message_at",
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "conversation_id",
        "sender_id",
        "short_body",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["conversation_id", "sender_id", "body"]
    readonly_fields = ["conversation_id", "sender_id", "created_at"]

    def short_body(self, obj):
        if not obj.body:
            return ""
        return f"{obj.body[:35]}..."

    short_body.short_description = "Body"
