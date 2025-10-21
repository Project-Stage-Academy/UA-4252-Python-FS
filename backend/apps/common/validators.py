from django.core.exceptions import ValidationError

def validate_file_size(file, max_size_mb):
    max_size = max_size_mb * 1024 * 1024
    if getattr(file, "size", 0) > max_size:
        raise ValidationError(f"Розмір файлу не може перевищувати {max_size_mb} MБ.")

def validate_file_type(file, allowed_types):
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        raise ValidationError(f"Файл повинен бути одним з: {', '.join(allowed_types)}.")