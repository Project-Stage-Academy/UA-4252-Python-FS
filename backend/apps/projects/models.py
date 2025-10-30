from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
import uuid
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify
from django.conf import settings

from django.db import IntegrityError, transaction
from django.utils import timezone


from apps.common.models import TimeStampedModel

PROJECT_STATUS = (
    ('idea', 'Idea'),
    ('mvp', 'MVP'),
    ('fundraising', 'Fundraising'),
    ('closed', 'Closed'),
)
VISIBILITY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private'),
    ('unlisted', 'Unlisted')
)


class Project(TimeStampedModel):
    startup = models.ForeignKey(
        "startups.StartupProfile",
        on_delete=models.CASCADE,
        related_name="projects",
        db_index=True,
    )
    title = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, blank=True, max_length=255)

    short_description = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='idea', db_index=True)

    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    currency = models.CharField(max_length=3, default="UAH")
    thumbnail = models.URLField(blank=True, null=True)

    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default="public"
    )

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_projects'
    )

    def clean(self):
        if self.target_amount < 0:
            raise ValidationError("Target amount cannot be negative.")
        if self.raised_amount < 0:
            raise ValidationError("Raised amount cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()

        if not self.slug:
            self.slug = slugify(self.title)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                break
            except IntegrityError:
                if attempt == max_retries - 1:
                    raise
                base_slug = slugify(self.title)
                counter = attempt + 1
                self.slug = f"{base_slug}-{counter}"

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return round((self.raised_amount / self.target_amount) * 100, 2)
        return 0.0

    def __str__(self):
        return self.title

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        indexes = [
            models.Index(fields=['startup', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_deleted'])
        ]


class ProjectAttachment(TimeStampedModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="attachments"
    )

    # When will be ready Upload models
    # upload = models.ForeignKey('uploads.Upload', on_delete=models.CASCADE)
    file = models.FileField(upload_to="project_attachments/%Y/%m")

    type = models.CharField(max_length=20)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project Attachment"
        verbose_name_plural = "Project Attachments"
        ordering = ["order", "-created_at"]


class ProjectAudit(models.Model):
    # project FK, user FK, timestamp, changes JSON
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="audit_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    changes = models.JSONField()

    user_agent = models.TextField(blank=True)

    def __str__(self):
        username = self.user.email if self.user else "System"
        return f"{self.project.title} - {self.action} by {username}"

    class Meta:
        verbose_name = "Project Audit Log"
        verbose_name_plural = "Project Audit Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["project", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]
