from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.startups.models import StartupProfile
import uuid

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
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(max_length=500)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='idea')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="UAH")
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['startup', 'status'']),
            models.Index(fields=['created_at'])
        ]
