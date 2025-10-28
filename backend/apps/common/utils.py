import os
import uuid


def logo_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    user_id = getattr(getattr(instance, 'user', None), 'id', None)
    user_uuid = str(user_id) if user_id else str(uuid.uuid4())
    filename = f"{user_uuid}{ext}"
    return os.path.join('logos', filename)
