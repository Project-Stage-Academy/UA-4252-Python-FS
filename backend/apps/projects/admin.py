from django.contrib import admin
from .models import Project, ProjectAttachment, ProjectAudit


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'startup', 'status', 'target_amount', 'raised_amount', 'created_at']
    list_filter = ['status', 'visibility', 'created_at']
    search_fields = ['title', 'slug', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    prepopulated_fields = {}

    fieldsets = (
        ('Basic info', {'fields': ('id', 'startup', 'title', 'slug')}),
        ('Description', {'fields': ('short_description', 'description')}),
        ('Funding', {'fields': ('target_amount', 'raised_amount', 'currency', 'status')}),
        ('Settings', {'fields': ('tags', 'visibility')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)})
    )


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'type', 'order', 'caption', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['id', 'created_at']

@admin.register(ProjectAudit)
class ProjectAuditAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['project__title', 'user__email']
    readonly_fields = ['id', 'project', 'user', 'action', 'timestamp', 'changes', 'user_agent']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
