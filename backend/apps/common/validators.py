import os

from PIL import Image, UnidentifiedImageError
from rest_framework import serializers


def drf_validate_file_size(file, max_size_mb):
    max_size = max_size_mb * 1024 * 1024
    if getattr(file, "size", 0) > max_size:
        raise serializers.ValidationError(
            f"Розмір файлу не може перевищувати {max_size_mb} MБ."
        )


def drf_validate_file_type(file, allowed_types):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_types:
        raise serializers.ValidationError(
            f"Дозволені розширення: {', '.join(allowed_types)}."
        )
    try:
        Image.open(file).verify()
        file.seek(0)
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise serializers.ValidationError("Invalid image file.") from e
