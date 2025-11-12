import os
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


def logo_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    user_id = getattr(getattr(instance, 'user', None), 'id', None)
    user_uuid = str(user_id) if user_id else str(uuid.uuid4())
    filename = f"{user_uuid}{ext}"
    return os.path.join('logos', filename)


def build_limit_choices(allowed_map: dict) -> Q:
    """
    Builds a Q() object to limit ContentType choices
    based on dict values like: {"alias": "app_label.model_name"}.
    """
    q = Q()

    for full_name in allowed_map.values():
        app_label, model_name = full_name.split(".")
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            q |= Q(app_label=ct.app_label, model=ct.model)
        except ContentType.DoesNotExist:
            raise RuntimeError(f"ContentType not found for {full_name}")

    return q
