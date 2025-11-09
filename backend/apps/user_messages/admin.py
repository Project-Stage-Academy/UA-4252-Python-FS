from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'notification_type',
        'is_read',
        'created_at',
        'related_project_link'
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
    ]
    search_fields = [
        'title',
        'message',
        'user__company_name',
        'related_project__title'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'read_at',
    ]
    list_per_page = 50
    date_hierarchy = 'created_at'

    def related_project_link(self, obj):
        if obj.related_project:
            return obj.related_project.title
        return '-'
    related_project_link.short_description = 'Project'

    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'notification_type', 'title', 'message', 'link_url')
        }),
        ('Related Content', {
            'fields': ('related_project', 'related_user')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
