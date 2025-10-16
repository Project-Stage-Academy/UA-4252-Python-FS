import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model

from apps.startups.models import StartupProfile
from apps.investors.models import InvestorProfile

User = get_user_model()


class RegistrationTestCase(TestCase):
    """
    Test case for user registration endpoint
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'

    def test_successful_startup_registration(self):
        data = {
            'email': 'startup@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'startup',
            'company_name': 'Test name',
            'description': 'Great startup',
            'website': 'https://test.com',
            'phone': '+380123456789'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['email'], 'startup@example.com')
        self.assertEqual(response.data['detail'], 'Verification email sent.')

        user = User.objects.get(email='startup@example.com')
        self.assertFalse(user.is_active)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

        startup_profile = StartupProfile.objects.get(user=user)
        self.assertEqual(startup_profile.company_name, 'Test name')
        self.assertEqual(startup_profile.email, 'startup@example.com')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify', mail.outbox[0].subject)

    def test_successful_investor_registration(self):
        """
        Test successful registration of an investor user
        """
        data = {
            'email': 'investor@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'role': 'investor',
            'investment_range_min': 10000,
            'investment_range_max': 100000
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email='investor@example.com')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')

        investor_profile = InvestorProfile.objects.get(user=user)
        self.assertEqual(investor_profile.investment_range_min, 10000)
        self.assertEqual(investor_profile.email, 'investor@example.com')
        self.assertEqual(investor_profile.full_name, 'Jane Doe')

        self.assertEqual(len(mail.outbox), 1)

    def test_missing_first_name(self):
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'last_name': 'Doe',
            'role': 'startup',
            'company_name': 'Test'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)

    def test_missing_last_name(self):
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'role': 'startup',
            'company_name': 'Test'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', response.data)


    def test_weak_password_validation(self):
        """Test that weak passwords are rejected"""
        data = {
            'email': 'test@example.com',
            'password': '123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'startup',
            'company_name': 'Test'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_invalid_email_format(self):
        data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'startup',
            'company_name': 'Test'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_missing_required_field(self):
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'startup'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company_name', response.data)

    def test_investor_missing_investment_range(self):
        data = {
            'email': 'investor@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'investor'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('investment_range_min', response.data)

    def test_duplicate_email(self):
        User.objects.create_user(
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password='Pass123!',
        )

        data = {
            'email': 'existing@example.com',
            'password': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'startup',
            'company_name': 'Another Company'
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

        self.assertEqual(User.objects.filter(email='existing@example.com').count(), 1)


class EmailVerificationTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='Pass123!',
            is_active=False,
        )

        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.verify_url = f'/api/auth/verify/{self.uid}/{self.token}/'

    def test_successful_email_verification(self):
        response = self.client.get(self.verify_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Email verified successfully.')

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_invalid_token(self):
        invalid_url = f'/api/auth/verify/{self.uid}/invalid-token-123/'
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid', response.data['detail'])

    def test_invalid_uid(self):
        invalid_url = f'/api/auth/verify/invalid-uid/{self.token}/'
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid', response.data['detail'])

    def test_nonexistent_user(self):
        fake_uuid = uuid.uuid4()
        fake_uid = urlsafe_base64_encode(force_bytes(fake_uuid))
        invalid_url = f'/api/auth/verify/{fake_uid}/{self.token}/'
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
