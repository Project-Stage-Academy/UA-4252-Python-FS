import uuid
import os


def logo_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    user_uuid = None
    if hasattr(instance, 'user') and hasattr(instance.user, 'id'):
        user_uuid = str(instance.user.id)
    else:
        user_uuid = str(uuid.uuid4())

    filename = f"{user_uuid}{ext}"
    return os.path.join('logos', filename)