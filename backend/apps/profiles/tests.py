import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile

User = get_user_model()

URL_BASE = '/api/profiles/{id}/'


class ProfileViewSetTestCase(APITestCase):
    """Test suite for ProfileViewSet"""

    def setUp(self):
        """Set up test data before each test"""
        # Create users
        self.startup_user = User.objects.create_user(
            email='startup@example.com',
            password='testpass123',
            first_name='test',
            last_name='test_last',
        )
        self.investor_user = User.objects.create_user(
            email='investor@example.com',
            password='testpass123',
            first_name='test',
            last_name='test_last',
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='test',
            last_name='test_last',
        )
        # Create startup profile
        self.startup_profile = StartupProfile.objects.create(
            user=self.startup_user,
            company_name='Test Startup',
            email='startup@example.com',
            description='A test startup',
            website='https://teststartup.com',
            phone='+1234567890',
            city='San Francisco',
            address='123 Startup St',
            postal_code='94102',
            partners_brands='Brand A, Brand B',
            audit_status='pending',
            founded_year=2020,
            team_size=10,
        )

        # Create investor profile
        self.investor_profile = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name='Test Investor',
            email='investor@example.com',
            description='A test investor',
            website='https://testinvestor.com',
            phone='+380987654321',  # PhoneNumberField with UA region
            city='New York',
            address='456 Investor Ave',
            postal_code='10001',
            partners_brands='Brand C',
            audit_status='approved',
            full_name='John Investor',
            investment_range_min=Decimal('10000.00'),
            investment_range_max=Decimal('100000.00'),
            preferred_industries='Tech, Finance',
            country='USA',
            region=1,
        )

    # ==================== RETRIEVE TESTS ====================

    def test_retrieve_startup_profile_success(self):
        """Test successfully retrieving a startup profile"""
        self.client.force_authenticate(user=self.startup_user)

        url = URL_BASE.format(id=str(self.startup_profile.id))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Test Startup')
        self.assertEqual(response.data['founded_year'], 2020)
        self.assertEqual(response.data['team_size'], 10)
        self.assertIn('email', response.data)

    def test_retrieve_nonexistent_profile(self):
        """Test retrieving a profile that doesn't exist returns 404"""
        non_existent_uuid = uuid.uuid4()
        url = URL_BASE.format(id=non_existent_uuid)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        if hasattr(response, 'data'):
            self.assertEqual(response.data['detail'], 'Profile not found')

    # ==================== PARTIAL UPDATE TESTS ====================

    def test_partial_update_startup_profile_by_owner_success(self):
        """Test owner can partially update their startup profile"""
        self.client.force_authenticate(user=self.startup_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))

        data = {'company_name': 'Updated Startup Name', 'team_size': 15}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Updated Startup Name')
        self.assertEqual(response.data['team_size'], 15)

        # Verify database was updated
        self.startup_profile.refresh_from_db()
        self.assertEqual(self.startup_profile.company_name, 'Updated Startup Name')
        self.assertEqual(self.startup_profile.team_size, 15)

    def test_partial_update_investor_profile_by_owner_success(self):
        """Test owner can partially update their investor profile"""
        self.client.force_authenticate(user=self.investor_user)
        url = URL_BASE.format(id=str(self.investor_profile.id))

        data = {'full_name': 'Jane Investor', 'investment_range_min': '20000.00'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Jane Investor')
        self.assertEqual(str(response.data['investment_range_min']), '20000.00')

        # Verify database was updated
        self.investor_profile.refresh_from_db()
        self.assertEqual(self.investor_profile.full_name, 'Jane Investor')
        self.assertEqual(
            self.investor_profile.investment_range_min, Decimal('20000.00')
        )

    def test_partial_update_by_unauthenticated_user_fails(self):
        """Test unauthenticated user cannot update profile (401)"""
        url = URL_BASE.format(id=str(self.startup_profile.id))
        data = {'company_name': 'Hacked Name'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verify database was not updated
        self.startup_profile.refresh_from_db()
        self.assertEqual(self.startup_profile.company_name, 'Test Startup')

    def test_partial_update_by_non_owner_fails(self):
        """Test non-owner cannot update profile (403)"""
        self.client.force_authenticate(user=self.other_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))
        data = {'company_name': 'Unauthorized Change'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify database was not updated
        self.startup_profile.refresh_from_db()
        self.assertEqual(self.startup_profile.company_name, 'Test Startup')

    def test_partial_update_with_invalid_data_returns_400(self):
        """Test partial update with invalid data returns 400"""
        self.client.force_authenticate(user=self.startup_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))

        # Test invalid team_size
        response = self.client.patch(url, {'team_size': 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid URL
        response = self.client.patch(url, {'website': 'not-a-valid-url'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_nonexistent_profile(self):
        """Test partial update of nonexistent profile returns 404"""
        self.client.force_authenticate(user=self.startup_user)
        non_existent_uuid = uuid.uuid4()
        url = URL_BASE.format(id=non_existent_uuid)
        data = {'company_name': 'Test'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        if hasattr(response, 'data'):
            self.assertEqual(response.data['detail'], 'Profile not found')

    # ==================== FULL UPDATE TESTS ====================

    def test_full_update_startup_profile_by_owner_success(self):
        """Test owner can fully update their startup profile"""
        self.client.force_authenticate(user=self.startup_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))

        data = {
            'company_name': 'Completely New Startup',
            'description': 'New description',
            'website': 'https://newstartup.com',
            'phone': '+1111111111',
            'city': 'Austin',
            'address': '789 New St',
            'postal_code': '78701',
            'partners_brands': 'New Brand',
            'audit_status': 'approved',
            'founded_year': 2022,
            'team_size': 25,
            'logo': None,
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Completely New Startup')
        self.assertEqual(response.data['city'], 'Austin')
        self.assertEqual(response.data['team_size'], 25)

    def test_full_update_by_unauthenticated_user_fails(self):
        """Test unauthenticated user cannot perform full update (401)"""
        url = URL_BASE.format(id=str(self.startup_profile.id))
        data = {
            'company_name': 'Hacked Company',
            'description': 'Hacked',
            'website': 'https://hacked.com',
            'phone': '+9999999999',
            'city': 'Nowhere',
            'address': '000 Hack St',
            'postal_code': '00000',
            'partners_brands': '',
            'audit_status': 'approved',
            'founded_year': 2020,
            'team_size': 1,
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_update_with_invalid_data_returns_400(self):
        """Test full update with missing required fields or invalid data returns 400"""
        self.client.force_authenticate(user=self.startup_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))

        # Missing required company_name
        response = self.client.put(
            url, {'description': 'Only description'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_update_nonexistent_profile_returns_404(self):
        """Test full update of nonexistent profile returns 404"""
        self.client.force_authenticate(user=self.startup_user)
        non_existent_uuid = uuid.uuid4()
        url = URL_BASE.format(id=non_existent_uuid)
        data = {
            'company_name': 'Test Company',
            'description': '',
            'website': '',
            'phone': '',
            'city': '',
            'address': '',
            'postal_code': '',
            'partners_brands': '',
            'audit_status': '',
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== EDGE CASES ====================

    def test_read_only_fields_cannot_be_updated(self):
        """Test that read-only fields (email) are not updated"""
        self.client.force_authenticate(user=self.startup_user)
        url = URL_BASE.format(id=str(self.startup_profile.id))

        original_email = self.startup_profile.email
        data = {'email': 'newemail@example.com', 'company_name': 'Updated Name'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], original_email)
        self.assertEqual(response.data['company_name'], 'Updated Name')

    # ==================== PUBLISH TESTS ====================

    def test_publish_complete_startup_profile_success(self):
        """Test successfully publishing a complete startup profile"""
        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_published'], True)
        self.assertIsNotNone(response.data['published_at'])
        self.assertEqual(response.data['published_by_id'], self.startup_user.id)

        # Verify database was updated
        self.startup_profile.refresh_from_db()
        self.assertTrue(self.startup_profile.is_published)
        self.assertIsNotNone(self.startup_profile.published_at)
        self.assertEqual(self.startup_profile.published_by_id, self.startup_user.id)

    def test_publish_complete_investor_profile_success(self):
        """Test successfully publishing a complete investor profile"""
        self.client.force_authenticate(user=self.investor_user)
        url = f'/api/profiles/{self.investor_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_published'], True)
        self.assertIsNotNone(response.data['published_at'])
        self.assertEqual(response.data['published_by_id'], self.investor_user.id)

        # Verify database
        self.investor_profile.refresh_from_db()
        self.assertTrue(self.investor_profile.is_published)

    def test_publish_incomplete_startup_profile_missing_required_fields(self):
        """Test publishing incomplete startup profile returns 400 with missing fields"""
        # Create incomplete profile (no logo added via test setup)
        incomplete_profile = StartupProfile.objects.create(
            user=self.startup_user,
            company_name='Incomplete Startup',
            email='incomplete@example.com',
            description='',  # Missing - required for publish
            founded_year=None,  # Missing - required for publish
            logo=None,  # Missing - required for publish
        )

        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{incomplete_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Profile incomplete')
        self.assertIn('missing_fields', response.data)
        self.assertIn('description', response.data['missing_fields'])
        self.assertIn('founded_year', response.data['missing_fields'])

        # Verify profile is NOT published
        incomplete_profile.refresh_from_db()
        self.assertFalse(incomplete_profile.is_published)

    def test_publish_incomplete_investor_profile_missing_required_fields(self):
        """Test publishing incomplete investor
        profile returns 400 with missing fields"""
        # Create incomplete profile
        incomplete_profile = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name='Incomplete Investor',
            email='incomplete_investor@example.com',
            description='',  # Missing - required for publish
            full_name='',  # Missing - required for publish
            investment_range_min=None,  # Missing - required for publish
            investment_range_max=None,  # Missing - required for publish
            preferred_industries='Tech',
            website='https://test.com',
            phone='+380987654321',
            country='USA',
            city='NYC',
            address='123 St',
            postal_code='10001',
            partners_brands='',
            audit_status='pending',
            logo=None,  # Missing - required for publish
        )

        self.client.force_authenticate(user=self.investor_user)
        url = f'/api/profiles/{incomplete_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Profile incomplete')
        self.assertIn('missing_fields', response.data)
        self.assertIn('description', response.data['missing_fields'])
        self.assertIn('full_name', response.data['missing_fields'])
        self.assertIn('investment_range_min', response.data['missing_fields'])
        self.assertIn('investment_range_max', response.data['missing_fields'])

        # Verify profile is NOT published
        incomplete_profile.refresh_from_db()
        self.assertFalse(incomplete_profile.is_published)

    def test_publish_already_published_profile_returns_400(self):
        """Test publishing already published profile returns 400"""
        # Publish profile first
        self.startup_profile.is_published = True
        self.startup_profile.save()

        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Profile is already published.')

    def test_publish_by_unauthenticated_user_fails(self):
        """Test unauthenticated user cannot publish profile (401)"""
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verify profile is NOT published
        self.startup_profile.refresh_from_db()
        self.assertFalse(self.startup_profile.is_published)

    def test_publish_by_non_owner_fails(self):
        """Test non-owner cannot publish profile (403)"""
        self.client.force_authenticate(user=self.other_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify profile is NOT published
        self.startup_profile.refresh_from_db()
        self.assertFalse(self.startup_profile.is_published)

    def test_publish_nonexistent_profile_returns_404(self):
        """Test publishing nonexistent profile returns 404"""
        self.client.force_authenticate(user=self.startup_user)
        non_existent_uuid = uuid.uuid4()
        url = f'/api/profiles/{non_existent_uuid}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_publish_sets_published_at_timestamp(self):
        """Test publish sets published_at timestamp"""
        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['published_at'])

        # Verify timestamp in database
        self.startup_profile.refresh_from_db()
        self.assertIsNotNone(self.startup_profile.published_at)

    def test_publish_updates_draft_saved_at(self):
        """Test publish updates draft_saved_at (via auto_now)"""
        original_draft_time = self.startup_profile.draft_saved_at

        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify draft_saved_at was updated (auto_now=True)
        self.startup_profile.refresh_from_db()
        self.assertGreater(self.startup_profile.draft_saved_at, original_draft_time)

    def test_only_owner_can_publish_their_profile(self):
        """Test only profile owner can publish their own profile"""
        # Owner publishes - should succeed
        self.client.force_authenticate(user=self.startup_user)
        url = f'/api/profiles/{self.startup_profile.id}/publish/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create another profile
        another_profile = StartupProfile.objects.create(
            user=self.other_user,
            company_name='Another Startup',
            email='another@example.com',
            description='Another description',
            founded_year=2021,
        )

        # Startup user tries to publish other user's profile - should fail
        url = f'/api/profiles/{another_profile.id}/publish/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify another_profile is NOT published
        another_profile.refresh_from_db()
        self.assertFalse(another_profile.is_published)
