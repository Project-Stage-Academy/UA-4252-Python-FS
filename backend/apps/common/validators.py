import os

from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
DOCUMENT_TYPES = ['.pdf', '.doc', '.docx']


def drf_validate_file_size(file, max_size_mb):
    max_size = max_size_mb * 1024 * 1024
    if getattr(file, "size", 0) > max_size:
        raise serializers.ValidationError(f"File size cannot exceed {max_size_mb} MB.")


def _verify_image_with_pil(file, check_image=True):
    if not check_image:
        return

    if getattr(file, "size", 0) == 0:
        raise serializers.ValidationError("File is empty.")

    try:
        Image.open(file).verify()
        file.seek(0)
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise serializers.ValidationError("Invalid image or corrupted file.") from e


def drf_validate_file_type(file, allowed_types):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_types:
        raise serializers.ValidationError(
            f"Allowed extensions: {', '.join(allowed_types)}."
        )
    if ext in IMAGE_TYPES:
        _verify_image_with_pil(file)


def drf_validate_attachment_file(file, max_size_mb=10):
    drf_validate_file_size(file, max_size_mb)
    ext = os.path.splitext(file.name)[1].lower()

    ALLOWED_TYPES = IMAGE_TYPES + DOCUMENT_TYPES

    if ext not in ALLOWED_TYPES:
        raise serializers.ValidationError(
            f'Support only the following formats: {", ".join(ALLOWED_TYPES)}.'
        )
    if ext in IMAGE_TYPES:
        _verify_image_with_pil(file)
