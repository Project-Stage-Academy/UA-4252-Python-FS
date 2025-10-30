import binascii
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db.models import UUIDField
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile

User = get_user_model()

ROLE_CHOICES = [
    ("startup", "Startup"),
    ("investor", "Investor"),
]


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password")


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration with role-specific fields.
    Supports two roles:
    - startup: requires company_name
    - investor: requires investment_range_min
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)

    # startup
    company_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    description = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # investor
    investment_range_min = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )
    investment_range_max = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True
    )

    def validate(self, data):
        """
        Validate role required fields
        """
        role = data.get("role")

        if role == "startup" and not data.get("company_name"):
            raise serializers.ValidationError(
                {"company_name": "This field is required for startups"}
            )

        elif role == "investor" and not data.get("investment_range_min"):
            raise serializers.ValidationError(
                {"investment_range_min": "This field is required for investors"}
            )

        return data

    def validate_email(self, value):
        """
        Check if email is already registered
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
        return value

    def create(self, validated_data):
        """
        Create user and profile based on role.
        """
        email = validated_data["email"]
        password = validated_data["password"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        role = validated_data["role"]

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )

        if role == "startup":
            StartupProfile.objects.create(
                user=user,
                company_name=validated_data.get("company_name", ""),
                description=validated_data.get("description", ""),
                website=validated_data.get("website", ""),
                phone=validated_data.get("phone", ""),
                email=email,
                founded_year=2024,
                team_size=1,
                city="",
                address="",
                postal_code="",
                logo="",
                partners_brands="",
                audit_status="Pending",
            )

        elif role == "investor":
            InvestorProfile.objects.create(
                user=user,
                company_name=validated_data.get("company_name", "Individual Investor"),
                full_name=f"{first_name} {last_name}",
                description="",
                investment_range_min=validated_data.get("investment_range_min"),
                investment_range_max=validated_data.get("investment_range_max"),
                preferred_industries="",
                website=validated_data.get("website", ""),
                email=email,
                phone=validated_data.get("phone", ""),
                country="Ukraine",
                region=8,
                city="",
                address="",
                postal_code="",
                logo="",
                partners_brands="",
                audit_status="Pending",
            )

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Validate format only without revealing existence.
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    re_new_password = serializers.CharField(min_length=8)

    @staticmethod
    def _get_user_from_uid(uid: str) -> User:
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uid))
        except (TypeError, ValueError, binascii.Error):
            raise serializers.ValidationError({"uid": "Invalid UID."})

        if isinstance(User._meta.pk, UUIDField):
            try:
                decoded_uid = UUID(decoded_uid)
            except ValueError:
                raise ValidationError({"uid": "Invalid UID."})

        user = User.objects.filter(pk=decoded_uid).first()
        if not user:
            raise serializers.ValidationError({"uid": "Invalid user ID."})

        return user

    def validate(self, attrs):
        """
        Checks performed:
        1. 'new_password' and 're_new_password' must match.
           - On mismatch, raises ValidationError:
             {'re_new_password': 'Passwords do not match.'}

        2. 'uid' must decode to a valid user.
           - On invalid UID format or non-existent user, raises ValidationError:
             {'uid': 'Invalid UID.'} or {'uid': 'Invalid user ID.'}

        3. 'token' must be a valid, non-expired password reset token for the user.
           - On invalid or expired token, raises ValidationError:
             {'token': 'Invalid or expired token.'}
        """
        if attrs["new_password"] != attrs["re_new_password"]:
            raise serializers.ValidationError(
                {"re_new_password": "Passwords do not match."}
            )

        user = self._get_user_from_uid(attrs["uid"])
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs) -> User:
        """
        Set a new password for the user after validation.
        Runs Django's password validators (validate_password).
            - On failure, raises ValidationError:
            {'new_password': [<list of validation error messages>]}
        """
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        user.set_password(new_password)
        user.save()
        return user


class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={"invalid": "Invalid format"})
