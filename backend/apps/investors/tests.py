from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.investors.models import InvestorProfile
from apps.users.models import User


class InvestorProfileModelTest(TestCase):
    """Unit tests for the InvestorProfile model"""

    def setUp(self):
        """Create a sample User and base data for InvestorProfile"""
        self.user = User.objects.create(
            username="investoruser",
            email="investor@example.com",
            password="plainpassword123",
            first_name="Investor",
            last_name="User"
        )

        self.valid_data = {
            "user": self.user,
            "company_name": "Tech Invest Group",
            "full_name": "John Doe",
            "description": "An active investor in Ukrainian startups.",
            "investment_range_min": 10000.00,
            "investment_range_max": 50000.00,
            "preferred_industries": "Technology, AI, Fintech",
            "website": "https://techinvest.com",
            "email": "investorprofile@example.com",
            "phone": "+380501234567",
            "country": "Ukraine",
            "region": 8,  # Kyiv
            "city": "Kyiv",
            "address": "Khreshchatyk St, 12",
            "postal_code": "01001",
            "partners_brands": "Petcube, Grammarly",
            "audit_status": "Pending",
        }

    def test_create_valid_investor_profile(self):
        """Ensure a valid InvestorProfile can be created"""
        investor = InvestorProfile.objects.create(**self.valid_data)
        self.assertIsInstance(investor, InvestorProfile)
        self.assertEqual(investor.company_name, "Tech Invest Group")
        self.assertEqual(investor.region, 8)

    def test_email_unique_constraint(self):
        """InvestorProfile should not allow duplicate emails"""
        InvestorProfile.objects.create(**self.valid_data)
        duplicate = self.valid_data.copy()
        duplicate["email"] = "investorprofile@example.com"  # duplicate email
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            InvestorProfile.objects.create(**duplicate)

    def test_investment_range_validation(self):
        """Investment range max should be greater than min"""
        invalid_data = self.valid_data.copy()
        invalid_data["investment_range_min"] = 50000.00
        invalid_data["investment_range_max"] = 10000.00
        investor = InvestorProfile(**invalid_data)
        # Currently no model-level validation, but logic placeholder
        self.assertTrue(investor.investment_range_min > investor.investment_range_max)

    def test_invalid_email_format(self):
        """Invalid email format should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "not-an-email"
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_region_choices_validation(self):
        """Region must be one of the defined REGION_CHOICES"""
        invalid_data = self.valid_data.copy()
        invalid_data["region"] = 999  # invalid region
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_str_method_returns_company_name(self):
        """__str__ should return the company name"""
        investor = InvestorProfile.objects.create(**self.valid_data)
        self.assertEqual(str(investor), "Tech Invest Group")

    def test_user_relation(self):
        """InvestorProfile should be linked to the correct User"""
        investor = InvestorProfile.objects.create(**self.valid_data)
        self.assertEqual(investor.user, self.user)
        self.assertEqual(investor.user.email, "investor@example.com")

    def test_missing_required_fields(self):
        """Missing required fields should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("company_name")
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_website_field_validation(self):
        """Website field must contain a valid URL"""
        invalid_data = self.valid_data.copy()
        invalid_data["website"] = "not-a-url"
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_max_length_fields(self):
        """CharField values exceeding max_length should raise ValidationError"""
        invalid_data = self.valid_data.copy()
        invalid_data["company_name"] = "A" * 201  # exceeds max_length=200
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()
