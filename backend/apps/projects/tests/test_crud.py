from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from apps.startups.models import StartupProfile
from apps.projects.models import Project

User = get_user_model()


class ProjectCRUDTestCase(TestCase):
    """Test cases for Project CRUD operations"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            first_name='Owner',
            last_name='Example',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            password='testpass123'
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='startup@example.com',
            description='Test description',
            phone='+380501234567',
            city='Kyiv'
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Short desc',
            description='<p>Full description</p>',
            target_amount=Decimal('50000.00'),
            currency='UAH',
            visibility='public'
        )

        self.client = APIClient()

        self.list_create_url = f'/api/startups/{self.startup.pk}/projects/'
        self.detail_url = f'/api/projects/{self.project.pk}/'

    def test_create_project_success(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Project',
            'description': '<p>New full description</p>',
            'target_amount': 100000,
            'currency': 'UAH',
            'tags': ['tech', 'innovation'],
            'visibility': 'public'
        }

        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Location', response)
        self.assertEqual(response.data['title'], 'New Project')
        self.assertEqual(response.data['target_amount'], '100000.00')
        self.assertEqual(response.data['raised_amount'], '0.00')

        self.assertEqual(Project.objects.count(), 2)
        project = Project.objects.get(title='New Project')
        self.assertEqual(project.startup, self.startup)

    def test_create_project_unauthorized(self):
        data = {
            'title': 'New Project',
            'short_description': 'Description',
            'target_amount': 50000,
            'currency': 'UAH',
        }

        response = self.client.post(self.list_create_url, data, format='json')

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_forbidden(self):
        self.client.force_authenticate(user=self.other_user)

        data = {
            'title': 'New Project',
            'short_description': 'Description',
            'target_amount': 50000,
            'currency': 'UAH',
        }

        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_invalid_amount(self):
        """Test creating project with invalid target amount"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Project',
            'short_description': 'Description',
            'target_amount': -1000,
            'currency': 'UAH',
        }

        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_amount', response.data)

    def test_list_projects_public(self):
        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['title'], 'Test Project')
        else:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['title'], 'Test Project')

    def test_list_projects_excludes_deleted(self):
        self.project.is_deleted = True
        self.project.deleted_by = self.user
        self.project.save()

        response = self.client.get(self.list_create_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 0)
        else:
            self.assertEqual(len(response.data['results']), 0)

    def test_retrieve_public_project(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')
        self.assertIn('description', response.data)
        self.assertIn('startup_name', response.data)
        self.assertIn('progress_percentage', response.data)

    def test_retrieve_private_project_unauthorized(self):
        """Test retrieving private project without auth returns 403"""
        self.project.visibility = 'private'
        self.project.save()

        response = self.client.get(self.detail_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_retrieve_private_project_as_owner(self):
        """Test owner can retrieve their private project"""
        self.project.visibility = 'private'
        self.project.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')

    def test_update_project_full_success(self):
        """Test full update (PUT) by owner"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Updated Project',
            'description': '<p>Updated description</p>',
            'target_amount': 75000,
            'currency': 'USD',
            'visibility': 'unlisted',
            'tags': ['updated'],
        }

        response = self.client.put(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Project')
        self.assertEqual(response.data['currency'], 'USD')

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Project')
        self.assertEqual(self.project.currency, 'USD')

    def test_update_project_partial_success(self):
        """Test partial update (PATCH) by owner"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Partially Updated Project',
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Partially Updated Project')

        self.project.refresh_from_db()
        self.assertEqual(self.project.short_description, 'Short desc')

    def test_update_project_forbidden(self):
        """Test non-owner cannot update project"""
        self.client.force_authenticate(user=self.other_user)

        data = {
            'title': 'Hacked Project',
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Test Project')

    def test_update_target_below_raised(self):
        """Test cannot set target amount below raised amount"""
        # Set some raised amount
        self.project.raised_amount = Decimal('30000.00')
        self.project.save()

        self.client.force_authenticate(user=self.user)

        data = {
            'target_amount': 20000,  # Less than raised
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_amount', response.data)

    def test_delete_project_success(self):
        """Test owner can delete project (soft delete)"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check soft delete - project still exists
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_deleted)
        self.assertIsNotNone(self.project.deleted_at)
        self.assertEqual(self.project.deleted_by, self.user)

        # Deleted project should not appear in listings
        list_response = self.client.get(self.list_create_url)
        if isinstance(list_response.data, list):
            self.assertEqual(len(list_response.data), 0)
        else:
            self.assertEqual(len(list_response.data['results']), 0)

    def test_delete_project_forbidden(self):
        """Test non-owner cannot delete project"""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check project still exists and not deleted
        self.project.refresh_from_db()
        self.assertFalse(self.project.is_deleted)

    def test_progress_percentage_calculation(self):
        """Test progress percentage is calculated correctly"""
        self.project.raised_amount = Decimal('25000.00')
        self.project.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percentage'], 50.0)

    def test_location_header_on_create(self):
        """Test Location header is returned on successful creation"""
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Project',
            'short_description': 'Description',
            'description': '<p>Full description</p>',
            'target_amount': 50000,
            'currency': 'UAH',
            'visibility': 'public',
        }

        response = self.client.post(self.list_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Location', response)
        self.assertIn('/api/projects/', response['Location'])


class ProjectSerializerTestCase(TestCase):
    """Test serializer fields"""

    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            first_name='Owner',
            last_name='User',
            password='testpass123'
        )

        self.startup = StartupProfile.objects.create(
            user=self.owner,
            company_name='Test Startup',
            description='Description',
            email='startup@test.com',
            phone='+380501234567',
            city='Kyiv',
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Short',
            description='<p>Full</p>',
            target_amount=Decimal('50000.00'),
            raised_amount=Decimal('10000.00'),
            currency='UAH',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_list_serializer_fields(self):
        """Test ProjectListSerializer has correct fields"""
        url = f'/api/startups/{self.startup.pk}/projects/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, list):
            data = response.data[0]
        else:
            data = response.data['results'][0]

        required_fields = [
            'id', 'title', 'slug', 'short_description',
            'target_amount', 'raised_amount', 'currency',
            'progress_percentage', 'startup_name', 'visibility',
            'created_at'
        ]

        for field in required_fields:
            self.assertIn(field, data, f"Field '{field}' missing in response")

    def test_detail_serializer_fields(self):
        """Test ProjectDetailSerializer has correct fields"""
        url = f'/api/projects/{self.project.pk}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        required_fields = [
            'id', 'startup_id', 'startup_name', 'email',
            'title', 'description', 'target_amount',
            'raised_amount', 'progress_percentage',
            'created_at', 'updated_at'
        ]

        for field in required_fields:
            self.assertIn(field, response.data, f"Field '{field}' missing in response")

    def test_progress_percentage_value(self):
        """Test progress_percentage is calculated correctly"""
        url = f'/api/projects/{self.project.pk}/'
        response = self.client.get(url)

        # 10000 / 50000 = 20%
        self.assertEqual(response.data['progress_percentage'], 20.0)

    def test_startup_name_correct(self):
        """Test startup_name comes from company_name field"""
        url = f'/api/projects/{self.project.pk}/'
        response = self.client.get(url)

        self.assertEqual(response.data['startup_name'], 'Test Startup')
