from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StartupProfile, InvestorProfile


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=['startup', 'investor'], required=True)

    # startup
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    short_pitch = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    # investor
    investment_range_min = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    investment_range_max = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    def validate(self, data):
        role = data.get('role')

        if role == 'startup':
            if not data.get('company_name'):
                raise serializers.ValidationError({
                    'company_name': 'This field is required for startups'
                })


        if role == 'investor':
            if not data.get('investment_range_min'):
                raise serializers.ValidationError({'investment_range_min': 'This field is required for investors'})
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
                short_pitch=validated_data.get('short_pitch', ''),
                website=validated_data.get('website', ''),
                phone=validated_data.get('phone', ''),
            )

        elif role == 'investor':
            InvestorProfile.objects.create(
                user=user,
                investment_range_min=validated_data.get('investment_range_min'),
                investment_range_max=validated_data.get('investment_range_max')
            )

        return user
