from django.db import models
from apps.investors.models import InvestorProfile
from django.contrib.auth import get_user_model
from apps.projects.models import Project

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link_url = models.URLField(max_length=200)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_user', null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"