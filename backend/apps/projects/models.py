from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.startups.models import StartupProfile
import uuid
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify


User = get_user_model()

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


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='projects', db_index=True)
    title = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, blank=True, max_length=255)

    short_description = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='idea', db_index=True)

    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    currency = models.CharField(max_length=3, default="UAH")
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['startup', 'status']),
                                 models.Index(fields=['created_at'])
                                 ]


class ProjectAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')

    # When will be ready Upload models
    # upload = models.ForeignKey('uploads.Upload', on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_attachments/%Y/%m')

    type = models.CharField(max_length=20)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Project Attachment'
        verbose_name_plural = 'Project Attachments'
        ordering = ['order', 'created_at']


class ProjectAudit(models.Model):
    # project FK, user FK, timestamp, changes JSON
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['project', '-timestamp']),
            models.Index(fields=['user', '-timestamp'])
        ]
