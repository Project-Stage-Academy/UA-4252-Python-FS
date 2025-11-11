from django.core.validators import MinValueValidator
from rest_framework import serializers

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile


class UnifiedProfileSerializer(serializers.Serializer):
    # Common fields for Startups and Investors

    company_name = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    description = serializers.CharField(allow_blank=True)
    website = serializers.URLField(allow_blank=True)
    phone = serializers.CharField(allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    address = serializers.CharField(allow_blank=True)
    postal_code = serializers.CharField(allow_blank=True)
    logo = serializers.ImageField(allow_null=True, allow_empty_file=True)
    partners_brands = serializers.CharField(allow_blank=True)
    audit_status = serializers.CharField(allow_blank=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Exceptional fields for Startups

    founded_year = serializers.IntegerField(
        allow_null=True, validators=[MinValueValidator(1900)], required=False
    )
    team_size = serializers.IntegerField(allow_null=True, required=False)

    # Exceptional fields for Investors

    full_name = serializers.CharField(required=False)
    investment_range_min = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    investment_range_max = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    preferred_industries = serializers.CharField(required=False)
    country = serializers.CharField(allow_blank=True, required=False)
    region = serializers.IntegerField(required=False)

    def to_representation(self, instance):
        """Dynamically formatting fields from profile type."""

        if isinstance(instance, StartupProfile):
            profile_type = 'startup'
        elif isinstance(instance, InvestorProfile):
            profile_type = 'investor'
        else:
            profile_type = 'unknown'

        # Basic fields
        data = {
            'company_name': instance.company_name,
            'email': instance.email,
            'description': instance.description,
            'website': instance.website,
            'phone': str(instance.phone) if instance.phone else '',
            'city': instance.city,
            'address': instance.address,
            'postal_code': instance.postal_code,
            'logo': instance.logo.url if instance.logo else None,
            'partners_brands': instance.partners_brands,
            'audit_status': instance.audit_status,
        }

        # Exceptional fields for Startups
        if profile_type == 'startup':
            data.update(
                {
                    'founded_year': getattr(instance, 'founded_year', None),
                    'team_size': getattr(instance, 'team_size', None),
                }
            )

        # Exceptional fields for Investors
        elif profile_type == 'investor':
            data.update(
                {
                    'investment_range_min': getattr(
                        instance, 'investment_range_min', None
                    ),
                    'investment_range_max': getattr(
                        instance, 'investment_range_max', None
                    ),
                    'full_name': getattr(instance, 'full_name', None),
                    'preferred_industries': getattr(
                        instance, 'preferred_industries', None
                    ),
                    'country': getattr(instance, 'country', None),
                    'region': getattr(instance, 'region', None),
                }
            )

        return data


class UnifiedProfileUpdateSerializer(serializers.Serializer):
    # Common fields for Startups and Investors

    company_name = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    description = serializers.CharField(allow_blank=True)
    website = serializers.URLField(allow_blank=True)
    phone = serializers.CharField(allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    address = serializers.CharField(allow_blank=True)
    postal_code = serializers.CharField(allow_blank=True)
    logo = serializers.ImageField(allow_null=True, allow_empty_file=True)
    partners_brands = serializers.CharField(allow_blank=True)
    audit_status = serializers.CharField(allow_blank=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Exceptional fields for Startups

    founded_year = serializers.IntegerField(
        allow_null=True, validators=[MinValueValidator(1900)], required=False
    )
    team_size = serializers.IntegerField(allow_null=True, required=False)

    # Exceptional fields for Investors

    full_name = serializers.CharField(required=False)
    investment_range_min = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    investment_range_max = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    preferred_industries = serializers.CharField(required=False)
    country = serializers.CharField(allow_blank=True, required=False)
    region = serializers.IntegerField(required=False)

    def validate_team_size(self, value):
        """Валідація розміру команди"""
        if value is not None and value < 1:
            raise serializers.ValidationError("Team size must be at least 1")
        if value is not None and value > 5000:
            raise serializers.ValidationError("Team size seems unrealistic")
        return value
