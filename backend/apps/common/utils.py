
def logo_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    user_uuid = instance.user.id  
    filename = f"{user_uuid}.{ext}"
    return f"logos/{filename}"