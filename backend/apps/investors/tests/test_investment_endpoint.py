from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import uuid
from decimal import Decimal

from ..models import InvestorProfile, Investment
from apps.projects.models import Project
from apps.startups.models import StartupProfile

User = get_user_model()

class InvestmentAPITests(APITestCase):

    def setUp(self):
        self.startup_user = User.objects.create_user(
            email='startup@example.com',
            password='password123',
            first_name='Startup',
            last_name='User'
        )
        self.startup_profile = StartupProfile.objects.create(
            user=self.startup_user, 
            company_name='StartCo',
            email='startup_profile@example.com', 
            phone='+380990000001'
        )

        self.investor_user = User.objects.create_user(
            email='investor@example.com',
            password='password123',
            first_name='Investor',
            last_name='User'
        )
        InvestorProfile.objects.create(
            user=self.investor_user, 
            company_name='InvestCo', 
            full_name='Investor User',
            preferred_industries='Tech, SaaS',
            website='http://invest.com',
            email='investor_profile@example.com', 
            phone='+380990000002',
            country='Ukraine',
            city='Kyiv',
            address='Test Address 1',
            postal_code='01001'
        )

        self.other_investor = User.objects.create_user(
            email='other@example.com',
            password='password123',
            first_name='Other',
            last_name='Investor'
        )
        InvestorProfile.objects.create(
            user=self.other_investor, 
            company_name='OtherCo', 
            full_name='Other User',
            preferred_industries='Fintech',
            website='http://other.com',
            email='other_profile@example.com', 
            phone='+380990000003',
            country='Ukraine',
            city='Lviv',
            address='Test Address 2',
            postal_code='79000'
        )

        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            first_name='Admin',
            last_name='User'
        )

        self.project_public = Project.objects.create(
            title='Test Project',
            status='fundraising',
            visibility='public',
            target_amount=100000,
            startup=self.startup_profile
        )
        self.project_not_fundraising = Project.objects.create(
            title='Closed Project',
            status='completed',
            visibility='public',
            target_amount=50000,
            startup=self.startup_profile
        )
        self.project_private = Project.objects.create(
            title='Private Project',
            status='fundraising',
            visibility='private',
            target_amount=200000,
            startup=self.startup_profile
        )
        
        self.investment = Investment.objects.create(
            investor=self.investor_user,
            project=self.project_public,
            amount_committed=10000,
            currency='USD'
        )

        self.create_url = reverse('investment-list')
        self.detail_url = reverse('investment-detail', kwargs={'pk': self.investment.pk})
        self.list_url = reverse('investor-investments-list', kwargs={'id': self.investor_user.id})
        self.other_list_url = reverse('investor-investments-list', kwargs={'id': self.other_investor.id})


    def test_unauthorized_create_investment(self):
        data = {'project': self.project_public.id, 'amount_committed': 1000, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_investor_create_investment(self):
        self.client.force_authenticate(user=self.startup_user)
        
        data = {'project': self.project_public.id, 'amount_committed': 1000, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only users with an investor profile can perform this action.")

    def test_investor_create_investment_success(self):
        self.client.force_authenticate(user=self.investor_user)
        
        data = {
            'project': self.project_public.id, 
            'amount_committed': 5000, 
            'currency': 'USD',
            'meta': {'round': 'seed'}
        }
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Investment.objects.count(), 2)
        
        new_investment = Investment.objects.latest('created_at')
        self.assertEqual(new_investment.investor, self.investor_user)
        self.assertEqual(new_investment.amount_committed, 5000)
        self.assertEqual(new_investment.status, 'committed')

    def test_create_investment_invalid_amount(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'project': self.project_public.id, 'amount_committed': -100, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_investment_invalid_currency(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'project': self.project_public.id, 'amount_committed': 100, 'currency': 'US'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currency', response.data)

    def test_create_investment_project_not_fundraising(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'project': self.project_not_fundraising.id, 'amount_committed': 1000, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not currently fundraising", response.data['project'][0])

    def test_create_investment_project_not_public(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'project': self.project_private.id, 'amount_committed': 1000, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot invest", response.data['project'][0])

    def test_create_investment_project_not_found(self):
        self.client.force_authenticate(user=self.investor_user)
        invalid_uuid = uuid.uuid4()
        data = {'project': invalid_uuid, 'amount_committed': 1000, 'currency': 'USD'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not exist", str(response.data['project'][0]))

    def test_owner_update_investment_success(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'amount_invested': 5000, 'status': 'transferred', 'meta': {'note': 'updated'}}
        
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.investment.refresh_from_db()
        self.assertEqual(self.investment.amount_invested, 5000)
        self.assertEqual(self.investment.status, 'transferred')
        self.assertEqual(self.investment.meta['note'], 'updated')

    def test_non_owner_update_investment_forbidden(self):
        self.client.force_authenticate(user=self.other_investor)
        data = {'amount_invested': 5000}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_update_investment_success(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'status': 'cancelled'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.investment.refresh_from_db()
        self.assertEqual(self.investment.status, 'cancelled')

    def test_update_investment_unauthorized(self):
        data = {'status': 'completed'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_investment_forbidden_field(self):
        self.client.force_authenticate(user=self.investor_user)
        data = {'amount_committed': 99999, 'amount_invested': 1}
        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.investment.refresh_from_db()
        self.assertEqual(self.investment.amount_committed, 10000)
        self.assertEqual(self.investment.amount_invested, 1)

    def test_owner_list_investments_success(self):
        self.client.force_authenticate(user=self.investor_user)
        Investment.objects.create(
            investor=self.investor_user, project=self.project_public, amount_committed=1, currency='USD'
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_non_owner_list_investments_forbidden(self):
        self.client.force_authenticate(user=self.other_investor)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You can only view your own investments.")

    def test_admin_list_other_investments_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_investments_unauthorized(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_investments_is_empty_for_other_investor(self):
        self.client.force_authenticate(user=self.other_investor)
        response = self.client.get(self.other_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_get_investment_list_as_owner(self):
        self.client.force_authenticate(user=self.investor_user)
        response = self.client.get(self.create_url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.investment.id))

    def test_get_investment_list_as_other_investor(self):
        self.client.force_authenticate(user=self.other_investor)
        response = self.client.get(self.create_url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_investment_detail_as_owner(self):
        self.client.force_authenticate(user=self.investor_user)
        response = self.client.get(self.detail_url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount_committed'], "10000.00")

    def test_get_investment_detail_as_non_owner(self):
        self.client.force_authenticate(user=self.other_investor)
        response = self.client.get(self.detail_url) 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)