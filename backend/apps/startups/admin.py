from django.contrib import admin

from .models import SavedStartup, StartupProfile


@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = ["company_name", "user", "email", "created_at"]
    list_filter = ["company_name", "created_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic info", {"fields": ("user", "company_name", "email", "description")}),
        ("Company Details", {"fields": ("logo",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(SavedStartup)
class SavedStartupAdmin(admin.ModelAdmin):
    list_display = ["startup", "investor", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["startup__company_name", "investor__company_name"]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("startup", "investor")
