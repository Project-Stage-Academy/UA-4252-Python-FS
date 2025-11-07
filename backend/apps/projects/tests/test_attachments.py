import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import ProjectAttachment
from apps.startups.models import StartupProfile

User = get_user_model()


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

    def create_test_image(self, name='test.jpg', size=(100, 100)):
        buf = io.BytesIO()
        img = Image.new('RGB', size, color='red')
        img.save(buf, format='JPEG')
        buf.seek(0)
        return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')

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
        large_content = b'x' * (11 * 1024 * 1024)
        large_file = SimpleUploadedFile(
            'large.jpg', large_content, content_type='image/jpeg'
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
