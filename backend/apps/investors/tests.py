import uuid
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.investors.models import (
    Investment,
    InvestorProfile,
    PortfolioSnapshot,
    Tracking,
    SavedItem,
)
from apps.projects.models import Project
from apps.startups.models import StartupProfile

User = get_user_model()


# ======================================================================
# InvestorProfileModelTest
# ======================================================================


class InvestorProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='test',
            first_name='Investor',
            last_name='User',
        )
        self.profile_data = {
            'user': self.user,
            'company_name': 'Capital Fund',
            'full_name': 'C D',
            'description': 'Test Description',
            'investment_range_min': 10000.00,
            'investment_range_max': 500000.00,
            'preferred_industries': 'IT',
            'website': 'http://capital.com',
            'email': 'capital@test.com',
            'phone': '+380502222222',
            'country': 'UA',
            'region': 8,
            'city': 'Kyiv',
            'address': '2',
            'postal_code': '2',
            'logo': 'logo.png',
            'partners_brands': 'none',
        }
        self.investor = InvestorProfile.objects.create(**self.profile_data)

    def test_profile_creation(self):
        self.assertEqual(self.investor.company_name, 'Capital Fund')

    def test_str_representation(self):
        self.assertEqual(str(self.investor), 'Capital Fund')

    def test_validation_error_on_range(self):
        invalid_data = self.profile_data.copy()
        invalid_data['investment_range_min'] = 600000.00
        invalid_data['investment_range_max'] = 500000.00
        investor_invalid = InvestorProfile(**invalid_data)

        with self.assertRaises(ValidationError) as cm:
            investor_invalid.full_clean()

        self.assertIn(
            "Maximum investment must be greater than minimum investment.",
            str(cm.exception),
        )


# ======================================================================
# InvestmentModelTest
# ======================================================================


class InvestmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='invest@example.com',
            password='test',
            first_name='Test',
            last_name='Investor',
        )

        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name='Fund Corp',
            full_name='D E',
            investment_range_min=10,
            investment_range_max=100,
            preferred_industries='IT',
            website='http://fund.com',
            email='fund@test.com',
            phone='+380503333333',
            country='UA',
            city='Kyiv',
            address='2',
            postal_code='2',
            logo='logo.png',
            description='desc',
            partners_brands='none',
        )

        self.startup_user = User.objects.create_user(
            email='startup@example.com',
            password='test',
            first_name='Startup',
            last_name='Owner',
        )
        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name="Startup Test Name",
            email="startup@test.com",
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title="E-Commerce Platform",
            target_amount=Decimal('100000.00'),
        )
        self.investment = Investment.objects.create(
            investor=self.user,
            project=self.project,
            status='committed',
            amount_committed=150000.00,
            amount_invested=50000.00,
        )

    def test_investment_creation(self):
        self.assertEqual(self.investment.status, 'committed')
        self.assertEqual(self.investment.amount_committed, Decimal('150000.00'))

    def test_str_representation(self):
        investor_name = f"{self.user.first_name} {self.user.last_name}"
        expected_str = f"Investment in {self.project.title} by {investor_name}"
        self.assertEqual(str(self.investment), expected_str)

    def test_unique_investment_constraints(self):
        Investment.objects.create(
            investor=User.objects.create_user(
                email='new_invest@ex.com',
                password='t',
                first_name='New',
                last_name='Inv',
            ),
            project=self.project,
            status='committed',
            amount_committed=200000.00,
        )
        self.assertEqual(Investment.objects.count(), 2)


# ======================================================================
# TrackingModelTest
# ======================================================================


class TrackingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='track@example.com',
            password='test',
            first_name='Test',
            last_name='Tracker',
        )
        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name='Tracker Inc.',
            full_name='T I',
            investment_range_min=1,
            investment_range_max=10,
            preferred_industries='IT',
            website='http://track.com',
            email='track@test.com',
            phone='+380504444444',
            country='UA',
            city='Kyiv',
            address='2',
            postal_code='2',
            logo='logo.png',
            description='desc',
            partners_brands='none',
        )
        self.target_id = uuid.uuid4()
        self.tracking_data = {
            'investor': self.user,
            'target_type': 'project',
            'target_id': self.target_id,
            'source': 'manual',
        }
        self.tracking = Tracking.objects.create(**self.tracking_data)

    def test_tracking_creation(self):
        self.assertEqual(self.tracking.target_type, 'project')

    def test_str_representation(self):
        investor_name = f"{self.user.first_name} {self.user.last_name}"
        expected_str = f"Tracking {self.tracking.target_type} for {investor_name}"
        self.assertEqual(str(self.tracking), expected_str)

    def test_unique_tracking_constraints(self):
        with self.assertRaises(IntegrityError):
            Tracking.objects.create(**self.tracking_data)


# ======================================================================
# PortfolioSnapshotModelTest
# ======================================================================


class PortfolioSnapshotModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='snapshot@example.com',
            password='test',
            first_name='Test',
            last_name='Snapshot',
        )
        self.investor_profile = InvestorProfile.objects.create(
            user=self.user,
            company_name='Snapshots LLC',
            full_name='S L',
            investment_range_min=1,
            investment_range_max=10,
            preferred_industries='IT',
            website='http://snap.com',
            email='snap@test.com',
            phone='+380505555555',
            country='UA',
            city='Kyiv',
            address='2',
            postal_code='2',
            logo='logo.png',
            description='desc',
            partners_brands='none',
        )
        self.computed_at = timezone.make_aware(datetime(2023, 10, 26, 10, 0, 0))
        self.snapshot = PortfolioSnapshot.objects.create(
            investor=self.user,
            computed_at=self.computed_at,
            projects_count=5,
            total_committed=500000.00,
            total_invested=250000.00,
            summary={'kpi': 'data'},
        )

    def test_snapshot_creation(self):
        self.assertEqual(self.snapshot.projects_count, 5)

    def test_str_representation(self):
        investor_name = f"{self.user.first_name} {self.user.last_name}"
        expected_str = f"Snapshot for {investor_name} at {str(self.computed_at)}"
        self.assertEqual(str(self.snapshot), expected_str)

    def test_unique_portfolio_snapshot_constraints(self):
        with self.assertRaises(IntegrityError):
            PortfolioSnapshot.objects.create(
                investor=self.user,
                computed_at=self.computed_at,
                projects_count=1,
                total_committed=1.00,
                total_invested=1.00,
                summary={'kpi': 'data'},
            )


class SavedItemModelTest(TestCase):
    """Unit tests for the SavedItem model"""

    def setUp(self):
        """Create related objects for testing SavedStartup"""
        self.investor_user = User.objects.create_user(
            email="investor@example.com",
            password="password123",
            first_name="Investor",
            last_name="User",
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

        self.startup_user = User.objects.create_user(
            email="owner@smartvision.ai",
            password="password321",
            first_name="Owner",
            last_name="Smart",
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
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title="AI Assistant",
            slug="ai-assistant",
            short_description="SmartVision’s AI-powered assistant.",
            target_amount=200000.00,
            visibility="public",
        )

        self.startup_data = {
            "investor": self.investor,
            "target_object": self.startup,
        }

        self.project_data = {
            "investor": self.investor,
            "target_object": self.project,
        }

    def test_create_valid_saved_startup(self):
        """Ensure a valid SavedItem can be created for Startup"""
        saved = SavedItem.objects.create(**self.startup_data)
        self.assertIsInstance(saved, SavedItem)
        self.assertEqual(saved.investor.company_name, "Global Ventures")
        self.assertEqual(saved.target_object.company_name, "SmartVision")

    def test_str_method_for_startup(self):
        """__str__ should return readable text for Startup"""
        saved = SavedItem.objects.create(**self.startup_data)
        expected_str = "Saved SmartVision by Global Ventures"
        self.assertEqual(str(saved), expected_str)

    def test_missing_required_fields_for_startup(self):
        """Missing required fields should raise ValidationError for Startup"""
        invalid_data = self.startup_data.copy()
        invalid_data.pop("target_object")
        saved = SavedItem(**invalid_data)
        with self.assertRaises(ValidationError):
            saved.full_clean()

    def test_foreign_key_relations_for_startup(self):
        """SavedItem must have valid investor and startup relations"""
        saved = SavedItem.objects.create(**self.startup_data)
        self.assertEqual(saved.investor.user.email, "investor@example.com")
        self.assertEqual(saved.target_object.user.email, "owner@smartvision.ai")

    def test_create_valid_saved_project(self):
        """Ensure a valid SavedItem can be created for Project"""
        saved = SavedItem.objects.create(**self.project_data)
        self.assertIsInstance(saved, SavedItem)
        self.assertEqual(saved.investor.company_name, "Global Ventures")
        self.assertEqual(saved.target_object.title, "AI Assistant")
        self.assertEqual(saved.target_object.startup, self.startup)

    def test_str_method_for_project(self):
        """__str__ should return readable text for Project"""
        saved = SavedItem.objects.create(**self.project_data)
        expected_str = "Saved AI Assistant by Global Ventures"
        self.assertEqual(str(saved), expected_str)

    def test_missing_required_fields_for_project(self):
        """Missing required fields should raise ValidationError for Project"""
        invalid_data = self.project_data.copy()
        invalid_data.pop("target_object")
        saved = SavedItem(**invalid_data)
        with self.assertRaises(ValidationError):
            saved.full_clean()

    def test_foreign_key_relations_for_project(self):
        """SavedItem must have valid investor and project relations"""
        saved = SavedItem.objects.create(**self.project_data)
        self.assertEqual(saved.investor.user.email, "investor@example.com")
        self.assertEqual(saved.target_object.startup.company_name, "SmartVision")

    def test_investor_can_save_both_startup_and_project(self):
        """Investor can save both a Startup and one of its Projects"""
        saved_startup = SavedItem.objects.create(**self.startup_data)
        saved_project = SavedItem.objects.create(**self.project_data)

        self.assertEqual(SavedItem.objects.filter(investor=self.investor).count(), 2)
        self.assertNotEqual(saved_startup.target_object, saved_project.target_object)
        self.assertEqual(saved_startup.investor, saved_project.investor)


class SavedItemViewSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser1@example.com",
            password="Pass123",
            first_name="First",
            last_name="User",
        )

        self.other_user = User.objects.create_user(
            email="testuser2@example.com",
            password="Pass123",
            first_name="Second",
            last_name="User",
        )

        self.investor = InvestorProfile.objects.create(
            user=self.user,
            company_name="Investor Co",
            full_name="John Doe",
            description="Some description",
            investment_range_min=1000,
            investment_range_max=5000,
            preferred_industries="Tech",
            website="https://example.com",
            email="investor@example.com",
            phone="+380501112233",
            country="Ukraine",
            region=1,
            city="Kyiv",
            address="Main St 1",
            postal_code="01001",
            partners_brands="Partner A",
        )

        self.other_investor = InvestorProfile.objects.create(
            user=self.other_user,
            company_name="Other Co",
            full_name="Jane Smith",
            description="Some description",
            investment_range_min=1000,
            investment_range_max=2000,
            preferred_industries="Health",
            website="https://other.com",
            email="other@example.com",
            phone="+380501234567",
            country="Ukraine",
            region=1,
            city="Lviv",
            address="Street 5",
            postal_code="79000",
            partners_brands="None",
        )

        self.startup = StartupProfile.objects.create(
            user=self.other_user,
            company_name="StartupOne",
            email="startup@example.com"
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title="ProjectOne",
            slug="project-one",
            target_amount=10000,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.create_url = reverse(
            "saved-item-create",
            kwargs={"investor_id": str(self.investor.id)},
        )

    def test_save_startup_success(self):
        """Test investor can save a startup"""
        data = {
            "target_type": "startupprofile",
            "target_id": str(self.startup.id),
        }

        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertIn("id", response.data)
        self.assertIn("saved_at", response.data)

        saved_startup = SavedItem.objects.get(id=response.data["id"])
        self.assertEqual(saved_startup.investor, self.investor)
        self.assertEqual(saved_startup.target_object, self.startup)

    def test_save_project_success(self):
        """Test investor can save a project"""
        data = {
            "target_type": "project",
            "target_id": str(self.project.id),
        }

        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertIn("id", response.data)
        self.assertIn("saved_at", response.data)

        saved_project = SavedItem.objects.get(id=response.data["id"])
        self.assertEqual(saved_project.investor, self.investor)
        self.assertEqual(saved_project.target_object, self.project)

    def test_save_item_idempotent(self):
        """Test duplicate record is not created if already exists"""
        data = {
            "target_type": "project",
            "target_id": str(self.project.id),
        }

        res1 = self.client.post(self.create_url, data, format="json")
        self.assertEqual(res1.status_code, 201)

        res2 = self.client.post(self.create_url, data, format="json")
        self.assertEqual(res2.status_code, 201)

        self.assertEqual(SavedItem.objects.count(), 1)
        self.assertEqual(res1.data["id"], res2.data["id"])

    def test_save_item_invalid_target_id(self):
        """Test user cannot save not existing item"""
        payload = {
            "target_type": "project",
            "target_id": "doesnotexist",
        }

        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("target_id", response.data)

    def test_delete_saved_item_success(self):
        """Test investor can delete a saved item"""
        saved_item = SavedItem.objects.create(
            investor=self.investor,
            target_type=ContentType.objects.get_for_model(Project),
            target_id=self.project.id,
        )
        delete_url = reverse(
            "saved-item-delete",
            kwargs={
                "investor_id": str(self.investor.id),
                "saved_item_id": str(saved_item.id),
            },
        )

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(SavedItem.objects.filter(id=saved_item.id).exists())

    def test_cannot_save_item_for_other_investor(self):
        """Test user cannot save item for other investor"""
        url = reverse(
            "saved-item-create",
            kwargs={"investor_id": str(self.other_investor.id)}
        )
        data = {
            "target_type": "project",
            "target_id": str(self.project.id),
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_investors_saved_item(self):
        """Test user cannot delete item saved by other investor"""
        saved_item = SavedItem.objects.create(
            investor=self.other_investor,
            target_type=ContentType.objects.get_for_model(Project),
            target_id=self.project.id,
        )
        url = reverse(
            "saved-item-delete",
            kwargs={
                "investor_id": str(self.other_investor.id),
                "saved_item_id": str(saved_item.id),
            },
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavedItem.objects.filter(id=saved_item.id).exists())

    def test_save_item_auth_required(self):
        """Test unauthenticated user cannot save item"""
        self.client.logout()
        data = {
            "target_type": "project",
            "target_id": str(self.project.id)
        }

        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, 401)
