from rest_framework import serializers
from .models import Notification
# from apps.projects.serializers import ProjectSerializer


class NotificationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(
        source='related_project.title',
        read_only=True,
        allow_null=True
    )
    project_slug = serializers.CharField(
        source='related_project.slug',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'link_url',
            'related_project',
            'project_title',
            'project_slug',
            'is_read',
            'read_at',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'link_url',
            'related_project',
            'project_title',
            'project_slug',
            'created_at',
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notification as read."""
    is_read = serializers.BooleanField(default=True)
