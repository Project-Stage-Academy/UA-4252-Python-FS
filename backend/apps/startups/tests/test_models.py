import pytest
from django.contrib.auth import get_user_model
from django.db import models as dj_models

from apps.startups.models import StartupProfile
from apps.startups import apps

User = get_user_model()


def _get_model(app_label, model_name):
    """Import model by name, skip tests if не знайдено."""
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        pytest.skip(f"{model_name} model not found in {app_label} app")


def _guess_user_fk_field(model_cls):
    """Try to find a FK/O2O to User by common names or by type."""
    # 1) common names
    for name in ("user", "owner", "account"):
        try:
            field = model_cls._meta.get_field(name)
            if isinstance(
                field, (dj_models.ForeignKey, dj_models.OneToOneField)
            ) and issubclass(field.related_model, User):
                return name
        except Exception:
            pass
    for field in model_cls._meta.get_fields():
        if isinstance(
            field, (dj_models.ForeignKey, dj_models.OneToOneField)
        ) and issubclass(field.related_model, User):
            return field.name
    pytest.skip("No FK/OneToOne relation to User found on StartupProfile")


def _default_for_field(field):
    """Return a simple value for required fields based on field type."""
    if isinstance(field, (dj_models.CharField, dj_models.TextField)):
        return f"test_{field.name}"
    if isinstance(field, dj_models.BooleanField):
        return False if field.default is dj_models.NOT_PROVIDED else field.default
    if isinstance(
        field,
        (
            dj_models.IntegerField,
            dj_models.AutoField,
            dj_models.BigIntegerField,
            dj_models.SmallIntegerField,
        ),
    ):
        return 1
    if isinstance(field, dj_models.FloatField):
        return 1.0
    if isinstance(field, dj_models.JSONField):
        return {}
    if isinstance(field, dj_models.DateField):
        from datetime import date

        return date.today()
    if isinstance(field, dj_models.DateTimeField):
        from django.utils import timezone

        return timezone.now()
    if isinstance(field, dj_models.EmailField):
        return "test@example.com"
    return None


@pytest.mark.django_db
def test_startup_profile_creation_and_link():
    user = User.objects.create_user(
        email="founder@example.com",
        first_name="Founder",
        last_name="User",
        password="secret",
    )
    profile = StartupProfile.objects.create(
        user=user,
        founded_year=2024,
        team_size=1,
    )
    assert profile.user == user
    assert profile.pk is not None
