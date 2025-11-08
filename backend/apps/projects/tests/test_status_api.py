from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.startups.models import StartupProfile

User = get_user_model()


class StatusAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassw',
            first_name='Test',
            last_name='User',
        )
        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title='API test project',
            target_amount=Decimal('5000.00'),
            currency='UAH',
        )
        self.client.force_authenticate(user=self.user)

    def test_status_update_endpoint(self):
        url = reverse(
            'startup-projects-update-status',
            kwargs={'startup_pk': self.startup.id, 'pk': self.project.id},
        )
        data = {'status': 'mvp'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'mvp')

    def test_invalid_transition_returns_400(self):
        url = reverse(
            'startup-projects-update-status',
            kwargs={'startup_pk': self.startup.id, 'pk': self.project.id},
        )
        data = {'status': 'funded'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_force_override_by_owner(self):
        url = reverse(
            'startup-projects-update-status',
            kwargs={'startup_pk': self.startup.id, 'pk': self.project.id},
        )
        data = {'status': 'funded', 'force': True}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'funded')

        self.project.refresh_from_db()
        self.assertIsNotNone(self.project.funded_at)

    def test_non_owner_cannot_change_status(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='pass123',
            first_name='Other',
            last_name='User',
        )
        self.client.force_authenticate(user=other_user)

        url = reverse(
            'startup-projects-update-status',
            kwargs={'startup_pk': self.startup.id, 'pk': self.project.id},
        )
        data = {'status': 'mvp'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auto_funding_on_raised_amount_update(self):
        self.project.start_mvp()
        self.project.start_fundraising()
        self.project.save()

        url = reverse(
            'startup-projects-detail',
            kwargs={'startup_pk': self.startup.id, 'pk': self.project.id},
        )
        data = {'raised_amount': '5000.00'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.FUNDED)
        self.assertIsNotNone(self.project.funded_at)
