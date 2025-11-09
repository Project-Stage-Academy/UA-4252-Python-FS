from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import TimeStampedModel

User = get_user_model()

REGION_CHOICES = (
    (0, 'Vinnytsia Region'),
    (1, 'Volyn Region'),
    (2, 'Luhansk Region'),
    (3, 'Dnipropetrovsk Region'),
    (4, 'Donetsk Region'),
    (5, 'Zhytomyr Region'),
    (6, 'Zakarpattia Region'),
    (7, 'Zaporizhzhia Region'),
    (8, 'Ivano-Frankivsk Region'),
    (9, 'Kyiv City'),
    (10, 'Kyiv Region'),
    (11, 'Kirovohrad Region'),
    (12, 'Sevastopol City'),
    (13, 'Autonomous Republic of Crimea'),
    (14, 'Lviv Region'),
    (15, 'Mykolaiv Region'),
    (16, 'Odesa Region'),
    (17, 'Poltava Region'),
    (18, 'Rivne Region'),
    (19, 'Sumy Region'),
    (20, 'Ternopil Region'),
    (21, 'Kharkiv Region'),
    (22, 'Kherson Region'),
    (23, 'Khmelnytskyi Region'),
    (24, 'Cherkasy Region'),
    (25, 'Chernihiv Region'),
    (26, 'Chernivtsi Region'),
)


class InvestorProfile(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    description = models.TextField()
    investment_range_min = models.DecimalField(max_digits=12, decimal_places=2)
    investment_range_max = models.DecimalField(max_digits=12, decimal_places=2)
    preferred_industries = models.CharField(
        max_length=200
    )  # In the future, consider using other table for statuses
    website = models.URLField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    phone = PhoneNumberField(region="UA")
    country = models.CharField(max_length=100)
    region = models.IntegerField(
        choices=REGION_CHOICES,
        default=8,
    )
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)
    logo = models.ImageField(upload_to="media/Investor_logos/")
    partners_brands = models.TextField()
    audit_status = models.CharField(max_length=50, default="Pending")

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)
    published_by_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="published_profiles"
    )
    draft_saved_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.investment_range_max < self.investment_range_min:
            raise ValidationError(
                "Maximum investment must be greater than minimum investment."
            )

    def __str__(self):
        return self.company_name

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"
