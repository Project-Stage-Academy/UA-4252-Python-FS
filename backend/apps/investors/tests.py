from django.core.exceptions import ValidationError
from django.test import TestCase
from apps.investors.models import InvestorProfile
from apps.users.models import User


class InvestorProfileModelTest(TestCase):
    """Unit tests for the InvestorProfile model"""

    def setUp(self):
        """Create a base User and default valid InvestorProfile data"""
        self.user = User.objects.create(
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

    def test_valid_investor_profile_creation(self):
        """Should create InvestorProfile successfully with valid data"""
        investor = InvestorProfile.objects.create(**self.valid_data)
        self.assertIsInstance(investor, InvestorProfile)
        self.assertEqual(investor.company_name, "Tech Invest Group")
        self.assertEqual(investor.region, 8)
        self.assertEqual(str(investor), "Tech Invest Group")

    def test_email_unique_constraint(self):
        """Should not allow duplicate investor emails"""
        InvestorProfile.objects.create(**self.valid_data)
        duplicate = self.valid_data.copy()
        duplicate["email"] = "investorprofile@example.com"
        with self.assertRaises(Exception):
            InvestorProfile.objects.create(**duplicate)

    def test_investment_range_validation(self):
        """Should raise ValidationError if max < min"""
        invalid_data = self.valid_data.copy()
        invalid_data["investment_range_min"] = 50000.00
        invalid_data["investment_range_max"] = 10000.00
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.clean()  # should trigger validation logic

    def test_invalid_email_format(self):
        """Should raise ValidationError for invalid email format"""
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "not-an-email"
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_invalid_website_format(self):
        """Should raise ValidationError for invalid website format"""
        invalid_data = self.valid_data.copy()
        invalid_data["website"] = "invalid-url"
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_invalid_phone_format(self):
        """Should raise ValidationError for invalid phone number"""
        invalid_data = self.valid_data.copy()
        invalid_data["phone"] = "12345"  # not valid for UA region
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_invalid_region_choice(self):
        """Should raise ValidationError for invalid region number"""
        invalid_data = self.valid_data.copy()
        invalid_data["region"] = 999  # not in REGION_CHOICES
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_missing_required_field(self):
        """Should raise ValidationError when required fields are missing"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("company_name")
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_field_max_length_constraints(self):
        """Should raise ValidationError if field exceeds max_length"""
        invalid_data = self.valid_data.copy()
        invalid_data["company_name"] = "A" * 300  # exceeds max_length=200
        investor = InvestorProfile(**invalid_data)
        with self.assertRaises(ValidationError):
            investor.full_clean()

    def test_user_relation(self):
        """InvestorProfile should correctly link to its User"""
        investor = InvestorProfile.objects.create(**self.valid_data)
        self.assertEqual(investor.user.email, "investor@example.com")
        self.assertEqual(investor.user.first_name, "Investor")
