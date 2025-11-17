import os
import uuid


def logo_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    user_id = getattr(getattr(instance, 'user', None), 'id', None)
    user_uuid = str(user_id) if user_id else str(uuid.uuid4())
    filename = f"{user_uuid}{ext}"
    return os.path.join('logos', filename)


def build_limit_choices(allowed_map: dict) -> dict:
    """
    Builds a limit_choices_to dict with "app_label__in" and "model__in"
    keys to limit ContentType choices based on dict values
    like: {"alias": "app_label.model_name"}.
    """
    apps = set()
    models = set()

    for full_name in allowed_map.values():
        app_label, model_name = full_name.split(".")
        apps.add(app_label)
        models.add(model_name)

    return {
        "app_label__in": list(apps),
        "model__in": list(models),
    }
