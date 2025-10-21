import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from apps.projects.models import Project
from apps.startups.models import StartupProfile
from apps.users.models import User

from django.db import IntegrityError
from django.utils import timezone

from apps.projects.models import ProjectAttachment

from apps.projects.models import ProjectAudit


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
            "target_amount": Decimal('50000.00'),
            "raised_amount": Decimal('10000.00'),
            "currency": "USD",
            "tags": ["AI", "Pets", "IoT"],
            "visibility": "public",
        }

    def test_create_valid_project(self):
        """Ensure a valid Project can be created successfully"""
        project = Project.objects.create(**self.valid_data)
        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, "AI-driven Pet Tracker")
        self.assertEqual(project.currency, "USD")
        self.assertEqual(project.status, 'fundraising')

    def test_create_minimal_project(self):
        minimal_project = Project.objects.create(
            startup=self.startup,
            title='Minimal Project',
            slug='minimal-project',
            target_amount=Decimal('1000.00')
        )
        self.assertEqual(minimal_project.short_description, '')
        self.assertEqual(minimal_project.description, '')
        self.assertEqual(minimal_project.status, 'idea')
        self.assertEqual(minimal_project.currency, 'UAH')

    def test_project_uses_uuid_primary_key(self):
        project = Project.objects.create(**self.valid_data)
        self.assertIsInstance(project.id, uuid.UUID)
        self.assertIsNotNone(project.id)
        self.assertFalse(Project._meta.get_field('id').editable)

    def test_slug_auto_generated_from_title(self):
        project = Project.objects.create(
            startup=self.startup,
            title='My project',
            target_amount=Decimal('1000.00')
        )
        self.assertEqual(project.slug, 'my-project')

    def test_slug_auto_generated_handles_duplicates(self):
        project1 = Project.objects.create(
            startup=self.startup,
            title='Test project',
            target_amount=Decimal('1000.00')
        )
        project2 = Project.objects.create(
            startup=self.startup,
            title='Test project',
            target_amount=Decimal('2000.00')
        )
        self.assertEqual(project1.slug, 'test-project')
        self.assertEqual(project2.slug, 'test-project-1')

    def test_slug_unique_constraint(self):
        """Slug field must be unique"""
        Project.objects.create(**self.valid_data)
        duplicate = self.valid_data.copy()
        duplicate["slug"] = "ai-pet-tracker"  # duplicate slug
        with self.assertRaises(ValidationError):
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
        invalid_data['short_description'] = 'A' * 501
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_short_description_optional(self):
        data = self.valid_data.copy()
        data.pop('short_description')
        project = Project.objects.create(**data)
        self.assertEqual(project.short_description, '')

    def test_description_optional(self):
        data = self.valid_data.copy()
        data.pop('description')
        project = Project.objects.create(**data)
        self.assertEqual(project.description, '')

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

    def test_target_amount_zero_invalid(self):
        invalid_data = self.valid_data.copy()
        invalid_data['target_amount'] = Decimal('0.00')
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_target_amount_minimum_valid(self):
        data = self.valid_data.copy()
        data['target_amount'] = Decimal('0.01')
        project = Project.objects.create(**data)
        project.full_clean()
        self.assertEqual(project.target_amount, Decimal('0.01'))

    def test_raised_amount_cannot_be_negative(self):
        invalid_data = self.valid_data.copy()
        invalid_data['raised_amount'] = Decimal('-500.00')
        project = Project(**invalid_data)
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_raised_amount_can_be_zero(self):
        data = self.valid_data.copy()
        data['raised_amount'] = Decimal('0.00')
        project = Project.objects.create(**data)
        project.full_clean()
        self.assertEqual(project.raised_amount, Decimal('0.00'))

    def test_raised_amount_can_exceed_target(self):
        data = self.valid_data.copy()
        data['target_amount'] = Decimal('10000.00')
        data['raised_amount'] = Decimal('15000.00')
        project = Project.objects.create(**data)
        self.assertGreater(project.raised_amount, project.target_amount)

    def test_str_method_returns_title(self):
        """__str__ method should return the project title"""
        project = Project.objects.create(**self.valid_data)
        self.assertEqual(str(project), "AI-driven Pet Tracker")

    def test_startup_foreign_key_relation(self):
        """Project must be linked to a valid StartupProfile"""
        project = Project.objects.create(**self.valid_data)
        self.assertEqual(project.startup, self.startup)
        self.assertEqual(project.startup.company_name, "Petcube")

    def test_tags_field_allows_long_list(self):
        """Tags field should accept long comma-separated strings"""
        long_tags = [f"tag{i}" for i in range(100)]
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
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='test@test.com'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            target_amount=Decimal('1000.00')
        )

    def test_create_attachment(self):
        file = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")
        attachment = ProjectAttachment.objects.create(
            project=self.project,
            type='image',
            caption='Test image',
            order=1
        )
        self.assertIsInstance(attachment, ProjectAttachment)
        self.assertEqual(attachment.project, self.project)
        self.assertEqual(attachment.type, 'image')


class ProjectAuditModelTest(TestCase):
    """Unit tests for ProjectAudit model"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='startup@test.com'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            target_amount=Decimal('1000.00')
        )

    def test_create_audit_log(self):
        audit = ProjectAudit.objects.create(
            project=self.project,
            user=self.user,
            action='update',
            changes={
                'status': {
                    'old': 'idea',
                    'new': 'fundraising'
                }
            }
        )
        self.assertIsInstance(audit, ProjectAudit)
        self.assertEqual(audit.project, self.project)
        self.assertEqual(audit.user, self.user)
        self.assertEqual(audit.action, 'update')

    def test_audit_jsonfield_stores_changes(self):
        changes = {
            'title': {'old': 'Old', 'new': 'New'},
            'status': {'old': 'idea', 'new': 'mvp'}
        }
        audit = ProjectAudit.objects.create(
            project=self.project,
            user=self.user,
            action='update',
            changes=changes
        )

        audit.refresh_from_db()
        self.assertEqual(audit.changes['title']['old'], 'Old')
        self.assertEqual(audit.changes['status']['new'], 'mvp')
