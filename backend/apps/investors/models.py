import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.utils import logo_upload_to
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
    region = models.IntegerField(choices=REGION_CHOICES, default=8)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)
    logo = models.ImageField(upload_to=logo_upload_to, blank=True, null=True)
    partners_brands = models.TextField()
    audit_status = models.CharField(max_length=50, default="Pending")

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


# Tracking Model
class Tracking(TimeStampedModel):
    investor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tracking'
    )
    target_type = models.CharField(
        choices=[('startup', 'startup'), ('project', 'project')], max_length=32
    )
    target_id = models.UUIDField()  # FK via generic relation or separate FK fields
    source = models.CharField(
        max_length=32,
        null=True,
        choices=[
            ('manual', 'manual'),
            ('suggestion', 'suggestion'),
            ('import', 'import'),
        ],
    )
    meta = models.JSONField(null=True)  # optional metadata

    class Meta:
        unique_together = ('investor', 'target_type', 'target_id')
        indexes = [
            models.Index(fields=['investor']),
            models.Index(fields=['target_type', 'target_id']),
        ]
        verbose_name = "Tracking"
        verbose_name_plural = "Trackings"

    def __str__(self):
        investor_name = f"{self.investor.first_name} {self.investor.last_name}".strip()
        return f"Tracking {self.target_type} for {investor_name}"


# Investment Model
class Investment(TimeStampedModel):
    investor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='investments'
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.PROTECT, related_name='investments'
    )
    status = models.CharField(
        choices=[
            ('committed', 'committed'),
            ('transferred', 'transferred'),
            ('returned', 'returned'),
            ('cancelled', 'cancelled'),
        ],
        default='committed',
        max_length=50,
    )
    amount_committed = models.DecimalField(max_digits=18, decimal_places=2)
    amount_invested = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='UAH')
    meta = models.JSONField(null=True)  # notes, terms, round info

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Investment"
        verbose_name_plural = "Investments"

    def __str__(self):
        investor_name = f"{self.investor.first_name} {self.investor.last_name}".strip()

        return f"Investment in {self.project.title} by {investor_name}"


# PortfolioSnapshot Model
class PortfolioSnapshot(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    computed_at = models.DateTimeField()
    projects_count = models.IntegerField()
    total_committed = models.DecimalField(max_digits=18, decimal_places=2)
    total_invested = models.DecimalField(max_digits=18, decimal_places=2)
    summary = models.JSONField()  # precomputed KPIs

    def __str__(self):
        investor_name = f"{self.investor.first_name} {self.investor.last_name}".strip()
        return f"Snapshot for {investor_name} at {self.computed_at}"

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Portfolio Snapshot"
        verbose_name_plural = "Portfolio Snapshots"
        unique_together = ('investor', 'computed_at')
