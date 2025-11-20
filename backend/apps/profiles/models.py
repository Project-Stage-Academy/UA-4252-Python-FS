from django.contrib.auth import get_user_model
from django.db import models

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile

User = get_user_model()


class ProfileAudit(models.Model):
    startup = models.ForeignKey(
        StartupProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    investor = models.ForeignKey(
        InvestorProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()
