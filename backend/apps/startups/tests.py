from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.startups.models import StartupProfile, SavedStartup
from apps.users.models import User
from apps.investors.models import InvestorProfile


class StartupProfileModelTest(TestCase):
    """Unit tests for the StartupProfile model"""

    def setUp(self):
        """Create a test User for the startup profile"""
        self.user = User.objects.create(
            username="startupuser",
            email="startup@example.com",
            password="securepassword",
            first_name="Startup",
            last_name="Owner"
        )

        self.valid_data = {
            "user": self.user,
            "company_name": "SmartVision",
            "description": "An innovative startup focusing on AI-based vision systems.",
            "founded_year": 2021,
            "team_size": 12,
            "website": "https://smartvision.ai",
            "email": "info@smartvision.ai",
            "phone": "+380501234567",
            "city": "Lviv",
            "address": "Shevchenka St, 22",
            "postal_code": "79000",
            "logo": "media/startup_logos/smartvision.png",
            "partners_brands": "NVIDIA, Intel",
            "audit_status": "Approved",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }

    def test_create_valid_startup_profile(self):
        """Ensure a valid StartupProfile can be created"""
        startup = StartupProfile.objects.create(**self.valid_data)
        self.assertIsInstance(startup, StartupProfile)
        self.assertEqual(startup.company_name, "SmartVision")
        self.assertEqual(startup.city, "Lviv")

    def test_missing_required_field(self):
        """Missing required fields should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("company_name")
        startup = StartupProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            startup.full_clean()

    def test_invalid_website_url(self):
        """Invalid website URL should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["website"] = "invalid-url"
        startup = StartupProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            startup.full_clean()

    def test_founded_year_and_team_size_fields(self):
        """Check numeric fields accept only valid integer values"""
        startup = StartupProfile.objects.create(**self.valid_data)
        self.assertIsInstance(startup.founded_year, int)
        self.assertIsInstance(startup.team_size, int)
        self.assertGreaterEqual(startup.founded_year, 2000)

    def test_str_method_returns_company_name(self):
        """__str__ should return company name"""
        startup = StartupProfile.objects.create(**self.valid_data)
        self.assertEqual(str(startup), "SmartVision")

    def test_user_foreign_key_relation(self):
        """StartupProfile should be linked to a valid User"""
        startup = StartupProfile.objects.create(**self.valid_data)
        self.assertEqual(startup.user, self.user)
        self.assertEqual(startup.user.email, "startup@example.com")


class SavedStartupModelTest(TestCase):
    """Unit tests for the SavedStartup model"""

    def setUp(self):
        """Create related objects for testing SavedStartup"""
        self.investor_user = User.objects.create(
            username="investoruser",
            email="investor@example.com",
            password="password123",
            first_name="Investor",
            last_name="User"
        )

        self.investor = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name="Global Ventures",
            full_name="Investor Inc.",
            description="A venture fund investing in tech startups.",
            investment_range_min=10000.00,
            investment_range_max=50000.00,
            preferred_industries="AI, SaaS",
            website="https://globalventures.com",
            email="contact@globalventures.com",
            phone="+380441234567",
            country="Ukraine",
            region=8,
            city="Kyiv",
            address="Khreshchatyk 10",
            postal_code="01001",
            logo="media/Investor_logos/logo.png",
            partners_brands="Tesla, SpaceX",
            audit_status="Verified",
        )

        self.startup_user = User.objects.create(
            username="founderuser",
            email="owner@smartvision.ai",
            password="password321",
            first_name="Owner",
            last_name="Smart"
        )

        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name="SmartVision",
            description="AI-based startup.",
            founded_year=2021,
            team_size=10,
            website="https://smartvision.ai",
            email="info@smartvision.ai",
            phone="+380501112233",
            city="Lviv",
            address="Shevchenka 22",
            postal_code="79000",
            logo="media/startup_logos/smartvision.png",
            partners_brands="Google, Amazon",
            audit_status="Approved",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
        )

        self.valid_data = {
            "investor": self.investor,
            "startup": self.startup,
            "notes": "Potential collaboration opportunity for Series A investment.",
        }

    def test_create_valid_saved_startup(self):
        """Ensure a valid SavedStartup can be created"""
        saved = SavedStartup.objects.create(**self.valid_data)
        self.assertIsInstance(saved, SavedStartup)
        self.assertEqual(saved.investor.company_name, "Global Ventures")
        self.assertEqual(saved.startup.company_name, "SmartVision")

    def test_str_method_returns_readable_text(self):
        """__str__ should return readable text with both company names"""
        saved = SavedStartup.objects.create(**self.valid_data)
        expected_str = f"Saved SmartVision by Global Ventures"
        self.assertEqual(str(saved), expected_str)

    def test_missing_required_fields(self):
        """Missing required fields should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("notes")
        saved = SavedStartup(**invalid_data)
        with self.assertRaises(ValidationError):
            saved.full_clean()

    def test_foreign_key_relations(self):
        """SavedStartup must have valid investor and startup relations"""
        saved = SavedStartup.objects.create(**self.valid_data)
        self.assertEqual(saved.investor.user.email, "investor@example.com")
        self.assertEqual(saved.startup.user.email, "owner@smartvision.ai")
