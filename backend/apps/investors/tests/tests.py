import uuid
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.investors.models import (
    Investment,
    InvestorProfile,
    PortfolioSnapshot,
    Tracking,
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

class TrackingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.investor_user = User.objects.create_user(
            email='investor-tracker@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Investor',
        )
        self.investor_profile = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name='Tracker Inc.',
            full_name='T I',
            investment_range_min=1,
            investment_range_max=10,
            email='track@test.com',
            phone='+380504444444',
            description='desc',
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User',
        )

        self.startup = StartupProfile.objects.create(
            user=self.other_user, 
            company_name="Test Startup",
            email="startup@test.com",
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title="Test Project",
            target_amount=Decimal('10000.00'),
        )

        self.create_url = reverse('tracking-list')
        self.list_url = reverse(
            'investor-tracking-list',
            kwargs={'investor_id': str(self.investor_user.id)}
        )

    def test_create_tracking_startup_success(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {
            "target_type": "startup",
            "target_id": str(self.startup.id),
            "source": "manual"
        }
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tracking.objects.count(), 1)
        self.assertEqual(response.data['target_id'], str(self.startup.id))

    def test_create_tracking_idempotent(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {
            "target_type": "project",
            "target_id": str(self.project.id),
            "source": "manual"
        }
        
        response1 = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tracking.objects.count(), 1)
        tracking_id = response1.data['id']

        response2 = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Tracking.objects.count(), 1)
        self.assertEqual(response2.data['id'], tracking_id) 

    def test_create_tracking_invalid_target_id(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {
            "target_type": "startup",
            "target_id": str(uuid.uuid4()), # Неіснуючий UUID
            "source": "manual"
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("target_id", response.data)

    def test_delete_tracking_success(self):
        self.client.force_authenticate(user=self.investor_user)
        tracking = Tracking.objects.create(
            investor=self.investor_user,
            target_type="startup",
            target_id=self.startup.id
        )
        self.assertEqual(Tracking.objects.count(), 1)
        
        delete_url = reverse('tracking-detail', kwargs={'pk': tracking.pk})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tracking.objects.count(), 0)

    def test_delete_tracking_not_owner_forbidden(self):
        tracking = Tracking.objects.create(
            investor=self.investor_user,
            target_type="startup",
            target_id=self.startup.id
        )
        self.assertEqual(Tracking.objects.count(), 1)
        
        self.client.force_authenticate(user=self.other_user)
        delete_url = reverse('tracking-detail', kwargs={'pk': tracking.pk})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Tracking.objects.count(), 1) 

    def test_list_tracking_success_and_filtering(self):
        self.client.force_authenticate(user=self.investor_user)
        
        Tracking.objects.create(
            investor=self.investor_user,
            target_type="startup",
            target_id=self.startup.id
        )
        Tracking.objects.create(
            investor=self.investor_user,
            target_type="project",
            target_id=self.project.id
        )
        
        response_startup = self.client.get(self.list_url, {'type': 'startup'})
        self.assertEqual(response_startup.status_code, status.HTTP_200_OK)
        self.assertEqual(response_startup.data['count'], 1)
        self.assertEqual(
            response_startup.data['results'][0]['target_id'], str(self.startup.id)
        )
        self.assertIsNotNone(response_startup.data['results'][0]['target'])
        self.assertEqual(
            response_startup.data['results'][0]['target']['company_name'],
            self.startup.company_name
        )
        response_project = self.client.get(self.list_url, {'type': 'project'})
        self.assertEqual(response_project.status_code, status.HTTP_200_OK)
        self.assertEqual(response_project.data['count'], 1)
        self.assertEqual(
            response_project.data['results'][0]['target']['title'],
            self.project.title
        )

    def test_list_tracking_not_owner_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url, {'type': 'startup'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)