from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email address")
    is_verified = models.BooleanField(default=False, verbose_name="Email verified")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class StartupProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='startup_profile'
    )
    company_name = models.CharField(max_length=255, verbose_name="Company name")
    short_pitch = models.TextField(blank=True, verbose_name="Short pitch")
    website = models.URLField(blank=True, verbose_name="Website")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Contact phone")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Startup Profile"
        verbose_name_plural = "Startup Profiles"

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"


class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='investor_profile'
    )
    investment_range_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimum investment"
    )
    investment_range_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Maximum investment"
    )
    industries_of_interest = models.TextField(blank=True, verbose_name="Industries of interest")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"

    def __str__(self):
        return f"Investor: {self.user.email}"