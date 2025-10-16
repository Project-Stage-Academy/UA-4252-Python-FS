# projects/tests/test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.projects.models import  Project
from apps.startups.models import StartupProfile

User = get_user_model()

class ProjectAPITestCase(APITestCase):
    def setUp(self):
        # Створюємо тестового користувача
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )

        # Створюємо стартап
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Test Startup",
            description="Test description",
            founded_year=2022,
            team_size=5,
            website="https://teststartup.com",
            email="test@test.com",
            phone="1234567890",
            city="Test City",
            address="Test Address",
            postal_code="12345",
            logo="https://example.com/logo.jpg",
            partners_brands="Test Partners",
            audit_status="active"
        )

        # Створюємо проект з обов'язковим полем target_amount
        self.project = Project.objects.create(
            title="Test Project",
            slug="test-project",
            short_desc="Test project description",
            description="Test description of the project",
            status="active",
            target_amount=10000.00,  # Додаємо значення для target_amount
            raised_amount=0.00,
            currency="UAH",
            thumbnail="https://example.com/image.jpg",
            tags="test, project",
            visibility="public",
            startup=self.startup
        )

    def test_project_api(self):
        url = f'/api/startups/{self.startup.id}/projects/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Перевірка кількості проектів
