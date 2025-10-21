from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.startups.models import StartupProfile
from apps.projects.models import Project
from django.core.exceptions import ValidationError

User = get_user_model()

class ProjectModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="testpassword"
        )

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
        
        self.project = Project.objects.create(
            startup=self.startup,
            title="Test Project",
            slug="test-project",
            short_desc="Test short description",
            description="Test description of the project.",
            status="draft",
            target_amount=10000.00,
            raised_amount=5000.00,
            currency="UAH",
            thumbnail="https://example.com/image.jpg",
            tags="test, example",
            visibility="public"
        )

    def test_project_creation_and_fields(self):
        self.assertEqual(self.project.title, "Test Project")
        self.assertEqual(self.project.status, "draft")
        self.assertEqual(self.project.target_amount, 10000.00)
        self.assertEqual(self.project.raised_amount, 5000.00)
        self.assertEqual(self.project.currency, "UAH")
        self.assertEqual(self.project.thumbnail, "https://example.com/image.jpg")
        self.assertEqual(self.project.tags, "test, example")
        self.assertEqual(self.project.visibility, "public")
        self.assertEqual(self.project.startup, self.startup)
        self.assertEqual(self.project.slug, "test-project")

    def test_invalid_target_amount_and_raised_amount(self):
        with self.assertRaises(ValidationError):
            self.project.target_amount = -1000.00
            self.project.clean()

        with self.assertRaises(ValidationError):
            self.project.raised_amount = -1000.00
            self.project.clean()

    def test_status_choices(self):
        valid_statuses = ['draft', 'in_progress', 'completed']
        for status in valid_statuses:
            self.project.status = status
            self.project.save()
            self.assertEqual(self.project.status, status)

    def test_blank_fields(self):
        project_without_thumbnail = Project.objects.create(
            startup=self.startup,
            title="Test Project Without Thumbnail",
            slug="test-project-without-thumbnail",
            short_desc="Test short description",
            description="Test description of the project.",
            status="draft",
            target_amount=10000.00,
            raised_amount=5000.00,
            currency="UAH",
            thumbnail=None,
            tags="test, example",
            visibility="public"
        )

        self.assertIsNone(project_without_thumbnail.thumbnail)
