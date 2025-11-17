from django.contrib import admin
from .models import InvestorProfile, SavedItem


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'company_name',
        'user_email',
        'investment_range',
        'city',
        'created_at'
    ]
    list_filter = [
        'investment_range_min',
        'city',
        'created_at'
    ]
    search_fields = [
        'company_name',
        'user__email',
        'full_name',
        'email'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'

    def investment_range(self, obj):
        return f'{obj.investment_range_min} - {obj.investment_range_max}'

    investment_range.short_description = 'Investment Range'

    fieldsets = (
        ('Company Info', {
            'fields': ('id', 'user', 'company_name', 'full_name', 'email')
        }),
        ('Investment Profile', {
            'fields': ('investment_range_min', 'investment_range_max', 'description')
        }),
        ('Location', {
            'fields': ('city', 'logo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ["investor", "target_type", "target_object", "saved_at"]
    search_fields = ["investor__company_name"]
    readonly_fields = ["saved_at"]
    list_filter = ["target_type"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("investor")
