import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.projects.models import Project
from apps.startups.models import StartupProfile
from apps.users.models import User

from django.db import IntegrityError
from django.utils import timezone

from backend.apps.projects.models import ProjectAttachment


class ProjectModelTest(TestCase):
    """Unit tests for the Project model"""

    def setUp(self):
        """Create a test user and startup profile for project relation"""
        self.user = User.objects.create(
            email="startup@example.com",
            password="password123",
            first_name="Startup",
            last_name="User"
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name="Petcube",
            description="Smart devices for pets",
            founded_year=2013,
            team_size=50,
            website="https://petcube.com",
            email="info@petcube.com",
            phone="+380441234567",
            city="Kyiv",
            address="Khreshchatyk 1",
            postal_code="01001",
            logo="media/startup_logos/petcube.png",
            partners_brands="Google, Amazon",
            audit_status="Approved",
        )

        self.valid_data = {
            "startup": self.startup,
            "title": "AI-driven Pet Tracker",
            "slug": "ai-pet-tracker",
            "short_description": "A smart AI system to track your pet’s activity.",
            "description": "This project develops an AI-based tracker integrated with IoT devices.",
            "status": "fundraising",
            "target_amount": 50000.00,
            "raised_amount": 10000.00,
            "currency": "USD",
            "tags": ["AI, Pets, IoT"],
            "visibility": "public",
        }

    def test_create_valid_project(self):
        """Ensure a valid Project can be created successfully"""
        project = Project.objects.create(**self.valid_data)
        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, "AI-driven Pet Tracker")
        self.assertEqual(project.currency, "USD")
        self.assertEqual(project.status, 'fundraising')

    def test_project_uses_uuid_primary_key(self):
        project = Project.objects.create(**self.valid_data)
        self.assertIsInstance(project.id, uuid.UUID)
        self.assertIsNone(project.id)
        self.assertFalse(Project._meta.get_field('id').editable)

    def test_slug_unique_constraint(self):
        """Slug field must be unique"""
        Project.objects.create(**self.valid_data)
        duplicate = self.valid_data.copy()
        duplicate["slug"] = "ai-pet-tracker"  # duplicate slug
        with self.assertRaises(IntegrityError):
            Project.objects.create(**duplicate)

    def test_required_fields_validation(self):
        """Missing required fields should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("title")
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_invalid_status_choice(self):
        """Invalid status not in STATUS_CHOICES should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["status"] = "unknown-status"
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_invalid_visibility_choice(self):
        invalid_data = self.valid_data.copy()
        invalid_data['visibility'] = 'invalid-visibility'
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_short_description_max_length(self):
        invalid_data = self.valid_data.copy()
        invalid_data['short_description'] = 'A'* 501
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_title_max_length(self):
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = 'A' * 256
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_currency_max_length(self):
        invalid_data = self.valid_data.copy()
        invalid_data['currency'] = 'USDD'
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_created_at_auto_set(self):
        project = Project.objects.create(**self.valid_data)
        self.assertIsNotNone(project.created_at)
        self.assertLessEqual(
            project.created_at,
            timezone.now()
        )

    def test_update_at_auto_update(self):
        project = Project.objects.create(**self.valid_data)
        old_update_at = project.updated_at

        import time
        time.sleep(0.1)

        project.title = 'Updated Title'
        project.save()

        self.assertGreater(project.updated_at, old_update_at)

    def test_target_amount_positive(self):
        """Raised amount should not exceed target amount (business logic placeholder)"""
        invalid_data = self.valid_data.copy()
        invalid_data['target_amount'] = Decimal('-1000.00')
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_raised_amount_cannot_be_negative(self):
        invalid_data = self.valid_data.copy()
        invalid_data['raised_amount'] = Decimal('-500.00')
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_str_method_returns_title(self):
        """__str__ method should return the project title"""
        project = Project.objects.create(**self.valid_data)
        self.assertEqual(str(project), "AI-driven Pet Tracker")

    def test_startup_foreign_key_relation(self):
        """Project must be linked to a valid StartupProfile"""
        project = Project.objects.create(**self.valid_data)
        self.assertEqual(project.startup, self.startup)
        self.assertEqual(project.startup.company_name, "Petcube")

    def test_tags_field_allows_long_text(self):
        """Tags field should accept long comma-separated strings"""
        long_tags = ",".join([f"tag{i}" for i in range(100)])
        data = self.valid_data.copy()
        data["tags"] = long_tags
        project = Project.objects.create(**data)
        self.assertIn("tag99", project.tags)

    def test_tags_field_accepts_list(self):
        project = Project.objects.create(**self.valid_data)
        self.assertEqual(project.tags, ['AI', 'Pets', 'IoT'])
        self.assertIsInstance(project.tags, list)

class ProjectAttachmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            password='password123'
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            slug='test_project',
            short_discription='Test discription',
            target_amount=Decimal('10000.00')
        )

    def test_create_attachment(self):
        attachment = ProjectAttachment.objects.create(
            project=self.project,
            type='image',
            caption='Test image',
            order=1
        )
        self.assertIsInstance(attachment, ProjectAttachment)
        self.assertEqual(attachment.project, self.project)
        self.assertEqual(attachment.type, 'image')