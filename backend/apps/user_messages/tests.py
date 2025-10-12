from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.user_messages.models import Notification
from apps.investors.models import InvestorProfile
from apps.users.models import User
from apps.projects.models import Project
from apps.startups.models import StartupProfile


class NotificationModelTest(TestCase):
    """Unit tests for the Notification model"""

    def setUp(self):
        """Prepare all required related objects"""
        # Create investor user
        self.investor_user = User.objects.create(
            username="investoruser",
            email="investor@example.com",
            password="password123",
            first_name="Investor",
            last_name="User"
        )

        # Create startup user
        self.startup_user = User.objects.create(
            username="startupuser",
            email="startup@example.com",
            password="password456",
            first_name="Startup",
            last_name="Owner"
        )

        # Create startup profile
        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name="TechStart",
            description="An innovative AI startup.",
            founded_year=2021,
            team_size=10,
            website="https://techstart.ai",
            email="contact@techstart.ai",
            phone="+380441234567",
            city="Kyiv",
            address="Khreshchatyk 20",
            postal_code="01001",
            logo="media/startup_logos/techstart.png",
            partners_brands="NVIDIA, AWS",
            audit_status="Approved"
        )

        # Create investor profile
        self.investor = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name="VenturePlus",
            full_name="John Investor",
            description="Investment firm focusing on deep tech.",
            investment_range_min=20000.00,
            investment_range_max=100000.00,
            preferred_industries="AI, IoT, SaaS",
            website="https://ventureplus.com",
            email="info@ventureplus.com",
            phone="+380501112233",
            country="Ukraine",
            region=8,
            city="Kyiv",
            address="Khreshchatyk 12",
            postal_code="01001",
            partners_brands="Google, Amazon",
            audit_status="Verified"
        )

        # Create project
        self.project = Project.objects.create(
            startup=self.startup,
            title="AI Analytics System",
            slug="ai-analytics-system",
            short_description="AI-powered data analytics tool.",
            description="A scalable data platform using ML algorithms.",
            status="In Progress",
            target_amount=50000.00,
            raised_amount=10000.00,
            currency="USD",
            tags="AI, Data, Analytics",
            visibility="public"
        )

        self.valid_data = {
            "user": self.investor,
            "notification_type": "Project Update",
            "title": "New Investment Opportunity",
            "message": "TechStart has launched a new AI Analytics project!",
            "link_url": "https://platform.com/projects/ai-analytics-system",
            "related_user": self.startup_user,
            "related_project": self.project,
            "is_read": False,
        }

    def test_create_valid_notification(self):
        """Ensure a valid Notification can be created"""
        notification = Notification.objects.create(**self.valid_data)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.title, "New Investment Opportunity")
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.related_project.title, "AI Analytics System")

    def test_str_method_returns_title(self):
        """__str__ should return the notification title"""
        notification = Notification.objects.create(**self.valid_data)
        self.assertEqual(str(notification), "New Investment Opportunity")

    def test_missing_required_field(self):
        """Missing required fields should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("title")
        notification = Notification(**invalid_data)
        with self.assertRaises(ValidationError):
            notification.full_clean()

    def test_invalid_link_url(self):
        """Invalid link_url format should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["link_url"] = "not-a-valid-url"
        notification = Notification(**invalid_data)
        with self.assertRaises(ValidationError):
            notification.full_clean()

    def test_foreign_key_relations(self):
        """Foreign key relations must link to valid objects"""
        notification = Notification.objects.create(**self.valid_data)
        self.assertEqual(notification.user.company_name, "VenturePlus")
        self.assertEqual(notification.related_user.username, "startupuser")
        self.assertEqual(notification.related_project.slug, "ai-analytics-system")

    def test_is_read_default_false(self):
        """is_read should be False by default"""
        notification = Notification.objects.create(**self.valid_data)
        self.assertFalse(notification.is_read)

    def test_can_mark_as_read(self):
        """Notification can be marked as read"""
        notification = Notification.objects.create(**self.valid_data)
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)
