import io
import os

from django.test import TestCase
from PIL import Image
from rest_framework.serializers import ValidationError

from apps.common.validators import drf_validate_file_size, drf_validate_file_type


class FileValidatorTest(TestCase):
    """Unit tests for file validators"""

    def create_image_file(self, format="PNG", name="test.png", size=(10, 10)):
        buf = io.BytesIO()
        img = Image.new("RGB", size)
        img.save(buf, format=format)
        buf.name = name
        buf.seek(0)
        buf.size = buf.getbuffer().nbytes
        buf.content_type = f"image/{format.lower()}"
        return buf

    def test_validate_file_size_pass(self):
        file = self.create_image_file()
        drf_validate_file_size(file, max_size_mb=1)

    def test_validate_file_size_fail(self):
        file = self.create_image_file()
        file.size = 11 * 1024 * 1024  # 11 MB
        with self.assertRaises(ValidationError):
            drf_validate_file_size(file, max_size_mb=10)

    def test_validate_file_type_pass(self):
        file = self.create_image_file(format="PNG", name="test.png")
        drf_validate_file_type(file, allowed_types=[".png"])

    def test_validate_file_type_fail_extension(self):
        file = self.create_image_file(format="PNG", name="test.png")
        with self.assertRaises(ValidationError):
            drf_validate_file_type(file, allowed_types=[".jpg"])

    def test_validate_file_type_fail_content(self):
        bad_file = io.BytesIO(b"not an image")
        bad_file.name = "test.png"
        bad_file.size = len(bad_file.getbuffer())
        with self.assertRaises(ValidationError):
            drf_validate_file_type(bad_file, allowed_types=[".png"])

    def test_file_can_be_saved_after_validation(self):
        file = self.create_image_file(format="PNG", name="saved.png")
        drf_validate_file_size(file, max_size_mb=1)
        drf_validate_file_type(file, allowed_types=[".png"])
        out_path = "saved.png"
        with open(out_path, "wb") as out:
            out.write(file.read())
        img = Image.open(out_path)
        img.verify()
        os.remove(out_path)
