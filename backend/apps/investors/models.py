from django.db import models
from apps.users.models import User

REGION_CHOICES = (
    (0, 'Cherkasy'),
    (1, 'Chernihiv'),
    (2, 'Chernivtsi'),
    (3, 'Dnipropetrovsk'),
    (4, 'Donetsk'),
    (5, 'Ivano-Frankivsk'),
    (6, 'Kherson'),
    (7, 'Kharkiv'),
    (8, 'Kyiv'),
    (9, 'Kirovohrad'),
    (10, 'Lviv'),
    (11, 'Mykolaiv'),
    (12, 'Odesa'),
    (13, 'Poltava'),
    (14, 'Rivne'),
    (15, 'Sumy'),
    (16, 'Ternopil'),
    (17, 'Vinnytsia'),
    (18, 'Volyn'),
    (19, 'Zaporizhzhia'),
    (20, 'Zhytomyr'),
    (21, 'Zakarpattia'),
    (22, 'Zaporizhzhia'),
    (23, 'Luhansk'),
)


class InvestorProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    description = models.TextField()
    investment_range_min = models.DecimalField(max_digits=12, decimal_places=2)
    investment_range_max = models.DecimalField(max_digits=12, decimal_places=2)
    preferred_industries = models.CharField(max_length=200) # In the future, consider using other table for statuses
    website = models.URLField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=100)
    region = models.IntegerField(
        choices=REGION_CHOICES,
        default=8,
    )
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='media/Investor_logos/')
    partners_brands = models.TextField()
    audit_status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Investor Profile"
        verbose_name_plural = "Investor Profiles"
