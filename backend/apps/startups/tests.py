from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.startups.models import StartupProfile, SavedStartup
from apps.users.models import User
from apps.investors.models import InvestorProfile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import StartupProfile
from django.contrib.auth import get_user_model

User = get_user_model()

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


class StartupPublicProfileAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="startupuser1",
            email="startup@example.com1",
            password="securepassword1",
            first_name="Startup1",
            last_name="Owner1"
        )
        self.startup1 = StartupProfile.objects.create(
            user=self.user1,
            company_name="Test Startup One",
            description="First test startup.",
            founded_year=2024,
            team_size=10,
            website="http://test1.com",
            email="test1@startup.com",
            phone="1111111111",
            city="Test City One",
            partners_brands="tech, innovation",
            audit_status="approved"
        )

        self.user2 = User.objects.create(
            username="startupuser2",
            email="startup@example.com2",
            password="securepassword2",
            first_name="Startup2",
            last_name="Owner2"
        )
        self.startup2 = StartupProfile.objects.create(
            user=self.user2,
            company_name="Test Startup Two",
            description="Second test startup.",
            founded_year=2025,
            team_size=5,
            website="http://test2.com",
            email="test2@startup.com",
            phone="2222222222",
            city="Test City Two",
            partners_brands="saas, finance",
            audit_status="pending"
        )

    def test_get_existing_startup_profile(self):
        """
        Check that an existing startup profile can be retrieved.
        """
        url = reverse('startupprofile-detail', kwargs={'id': self.startup1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.startup1.company_name)
        self.assertIn('logo_url', response.data)
        self.assertEqual(response.data['tags'], ['tech', 'innovation'])
        self.assertEqual(response.data['followers_count'], 0)

    def test_get_correct_startup_profile_when_multiple_exist(self):
        """
        Check that the correct profile is returned when multiple exist.
        """
        url = reverse('startupprofile-detail', kwargs={'id': self.startup2.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], "Test Startup Two")
        self.assertNotEqual(response.data['company_name'], "Test Startup One")
        self.assertEqual(response.data['founded_year'], 2025)
        self.assertEqual(response.data['tags'], ['saas', 'finance'])

    def test_response_schema_is_correct(self):
        """
        Check that the API response contains all expected fields.
        """
        url = reverse('startupprofile-detail', kwargs={'id': self.startup1.id})
        response = self.client.get(url)
        
        expected_keys = [
            'id', 'company_name', 'description', 'founded_year', 'team_size',
            'website', 'email', 'phone', 'city', 'logo_url', 'tags',
            'followers_count', 'created_at'
        ]
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data.keys(), expected_keys)

    def test_get_non_existent_startup_profile(self):
        """
        Check that a 404 is returned for a non-existent startup.
        """
        url = reverse('startupprofile-detail', kwargs={'id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)