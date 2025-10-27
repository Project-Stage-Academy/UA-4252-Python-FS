from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class StartupProfile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="startup_profiles"
    )
    company_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100)

    description = models.TextField(blank=True, default="")

    founded_year = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(1900)]
    )
    team_size = models.IntegerField(blank=True, null=True, default=1)
    website = models.URLField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")

    # We need to craete media folder and set MEDIA_URL and MEDIA_ROOT in settings.py
    logo = models.ImageField(upload_to="startup_logos/%Y/%m/", blank=True, null=True)
    partners_brands = models.TextField(blank=True, default="")

    audit_status = models.CharField(max_length=100, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["company_name"]),
            models.Index(fields=["-created_at"]),
        ]


class SavedStartup(models.Model):
    investor = models.ForeignKey(
        "investors.InvestorProfile",
        on_delete=models.CASCADE,
        related_name="saved_startups",
    )
    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, related_name="saved_by_investors"
    )
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Saved {self.startup.company_name} by {self.investor.company_name}"

    class Meta:
        verbose_name = "Saved Startup"
        verbose_name_plural = "Saved Startups"
        unique_together = ["investor", "startup"]
        ordering = ["-created_at"]
