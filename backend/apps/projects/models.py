from django.db import models
from apps.startups.models import StartupProfile

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
)

class Project(models.Model):
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="UAH")
    tags = models.TextField()
    visibility = models.CharField(max_length=20, default="public")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"