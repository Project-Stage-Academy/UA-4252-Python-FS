import io
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.startups.models import StartupProfile

User = get_user_model()

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT) / 'test_media'


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProjectAttachmentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='startup@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        self.startup = StartupProfile.objects.create(
            user=self.user, company_name='Test Startup', email='startup@test.com'
        )

        self.client.force_authenticate(user=self.user)
        self.url = f'/api/startups/{self.startup.id}/projects/'

    def tearDown(self):
        if TEST_MEDIA_ROOT.exists():
            shutil.rmtree(TEST_MEDIA_ROOT)

    def create_test_image(self, name='test.jpg', size=(100, 100)):
        buf = io.BytesIO()
        img = Image.new('RGB', size, color='red')
        img.save(buf, format='JPEG')
        buf.seek(0)
        return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')

    def create_test_pdf(self, name='test.pdf'):
        pdf_content = (
            b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj '
            b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj '
            b'3 0 obj<</Type/Page/Parent 2 0 '
            b'R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/'
            b'BaseFont/Helvetica>>>>>>>/MediaBox[0 0 612 792]/'
            b'Contents 4 0 R>>endobj 4 0 obj<</Length 44>>stream\n'
            b'BT /F1 12 Tf 100 700 Td (Test PDF) Tj '
            b'ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 '
            b'f\n0000000009 00000 n\n0000000056 00000 n\n0000000115 '
            b'00000 n\n0000000324 00000 n\ntrailer<</Size 5/Root 1 '
            b'0 R>>\nstartxref\n406\n%%EOF'
        )
        return SimpleUploadedFile(name, pdf_content, content_type='application/pdf')

    def test_create_project_with_attachment(self):
        image = self.create_test_image()
        data = {
            'title': 'Project with Attachment',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': image,
            'captions': 'Test Image',
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachments', response.data)
        self.assertEqual(len(response.data['attachments']), 1)
        self.assertEqual(response.data['attachments'][0]['type'], 'image')

    def test_create_project_with_pdf_attachment(self):
        pdf_file = self.create_test_pdf()
        data = {
            'title': 'Project with PDF',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': pdf_file,
            'captions': 'Test PDF Document',
        }
        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attachments', response.data)
        self.assertEqual(len(response.data['attachments']), 1)
        self.assertEqual(response.data['attachments'][0]['type'], 'document')

    def test_corrupted_image_rejected(self):
        corrupted_image = SimpleUploadedFile(
            'corrupted.jpg',
            b'This is not a valid image file content',
            content_type='image/jpeg',
        )

        data = {
            'title': 'Corrupted Image Test',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': corrupted_image,
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_invalid_file_type_rejected(self):
        txt_file = SimpleUploadedFile('test.txt', b'content', content_type='text/plain')

        data = {
            'title': 'Invalid File Test',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': txt_file,
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_large_file_rejected(self):
        base_pdf = (
            b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 '
            b'obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 '
            b'obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1<</Type'
            b'/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>/MediaBox[0 '
            b'0 612 792]/Contents 4 0 R>>endobj 4 0 obj<</Length 44>>'
            b'stream\nBT /F1 12 Tf 100 700 Td (Test PDF) Tj '
            b'ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 '
            b'f\n0000000009 00000 n\n0000000056 00000 n\n0000000115 '
            b'00000 n\n0000000324 00000 n\ntrailer<</Size 5/Root 1 0 '
            b'R>>\nstartxref\n406\n%%EOF'
        )

        large_content = base_pdf + b'x' * (11 * 1024 * 1024)

        large_file = SimpleUploadedFile(
            'large.pdf', large_content, content_type='application/pdf'
        )

        data = {
            'title': 'Large File Test',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': large_file,
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_empty_file_rejected(self):
        empty_file = SimpleUploadedFile('empty.jpg', b'', content_type='image/jpeg')

        data = {
            'title': 'Empty File Test',
            'short_description': 'Test',
            'target_amount': 50000,
            'visibility': 'public',
            'attachments': empty_file,
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)
