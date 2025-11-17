from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.common.utils import logo_upload_to

User = get_user_model()


class StartupProfile(TimeStampedModel):
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
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    logo = models.ImageField(upload_to=logo_upload_to, blank=True, null=True)
    partners_brands = models.TextField(blank=True, default='')

    audit_status = models.CharField(max_length=100, blank=True, default="")

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_by_id = models.UUIDField(null=True, blank=True)
    draft_saved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["company_name"]),
            models.Index(fields=["-created_at"]),
            GinIndex(fields=["tags"], name="startups_tags_gin"),
        ]
