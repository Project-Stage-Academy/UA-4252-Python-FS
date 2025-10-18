import pytest
from backend.apps.startups.models import StartupProfile
from django.contrib.auth import get_user_model


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
            if isinstance(field, (models.ForeignKey, models.OneToOneField)) and issubclass(field.related_model, User):
                return name
        except Exception:
            pass
    # 2) any relation to User
    for field in model_cls._meta.get_fields():
        if isinstance(field, (models.ForeignKey, models.OneToOneField)) and issubclass(field.related_model, User):
            return field.name
    pytest.skip("No FK/OneToOne relation to User found on StartupProfile")


def _default_for_field(field):
    """Return a simple value for required fields based on field type."""
    if isinstance(field, (models.CharField, models.TextField)):
        return f"test_{field.name}"
    if isinstance(field, models.BooleanField):
        # respect default if defined
        return False if field.default is models.NOT_PROVIDED else field.default
    if isinstance(field, (models.IntegerField, models.AutoField, models.BigIntegerField, models.SmallIntegerField)):
        return 1
    if isinstance(field, models.FloatField):
        return 1.0
    if isinstance(field, models.JSONField):
        return {}
    if isinstance(field, models.DateField):
        from datetime import date
        return date.today()
    if isinstance(field, models.DateTimeField):
        from django.utils import timezone
        return timezone.now()
    if isinstance(field, models.EmailField):
        return "test@example.com"
    return None


@pytest.mark.django_db
def test_startup_profile_creation_and_link():
    user = User.objects.create_user(username="founder", password="secret")
    profile = StartupProfile.objects.create(user=user)
    assert profile.user == user
    assert profile.pk is not None
