from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StartupProfile, InvestorProfile


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=['startup', 'investor'], required=True)

    company_name = serializers.CharField(max_length=255, required=True, allow_blank=True)

    description = serializers.CharField(max_length=255, required=False, allow_blank=True)
    founded_year = serializers.IntegerField(required=False, allow_null=True)
    team_size = serializers.IntegerField(required=False, allow_null=True)

    website = serializers.URLField(required=False, allow_blank=True)

    # startup
    phone = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.CharField(required=False, allow_blank=True)
    partners_brand = serializers.CharField(required=False, allow_blank=True)
    audit_status = serializers.CharField(required=False, allow_blank=True)

    # investor
    investment_range_min = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    investment_range_max = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    def validate(self, data):
        role = data.get('role')

        if role == 'investor':
            if not data.get('investment_range_min'):
                raise serializers.ValidationError({'investment_range_min': 'This field is required for startups'})
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        role = validated_data['role']

        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=False,
            username=email
        )

        if role == 'startup':
            StartupProfile.objects.create(
                user=user,
                company_name=validated_data.get('company_name', ''),
                website=validated_data.get('website', ''),
                phone=validated_data.get('phone', ''),
            )

        elif role == 'investor':
            InvestorProfile.objects.create(
                user=user,
                investment_range_min=validated_data.get('investment_range_min', 0),
                investment_range_max=validated_data.get('investment_range_max', 0)
            )

        return user
