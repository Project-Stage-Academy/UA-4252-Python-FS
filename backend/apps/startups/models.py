from django.db import models
from apps.users.models import User
from apps.investors.models import InvestorProfile


class StartupProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    founded_year = models.IntegerField()
    team_size = models.IntegerField()
    website = models.URLField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    # We need to craete media folder and set MEDIA_URL and MEDIA_ROOT in settings.py
    logo = models.ImageField(upload_to='media/startup_logos/')
    partners_brands = models.TextField()
    audit_status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"


class SavedStartup(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE)
    notes = models.TextField()

    def __str__(self):
        return f'Saved {self.startup.company_name} by {self.investor.company_name}'

    class Meta:
        verbose_name = "Saved Startup"
        verbose_name_plural = "Saved Startups"
