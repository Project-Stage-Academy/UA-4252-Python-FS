"""
Tests cover:
1. Create permissions (IsStartupOwner)
2. Update/Delete permissions (IsOwnerOrReadOnly)
3. View permissions based on visibility (CanViewProject)
4. Unauthorized access and privilege escalation attempts
5. Status update permissions
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.startups.models import StartupProfile

User = get_user_model()


@pytest.fixture
def api_client():
    """API client for making requests"""
    return APIClient()


@pytest.fixture
def owner_user(db):
    """User who owns a startup"""
    return User.objects.create_user(
        email='owner@example.com',
        password='testpass123',
        first_name='Owner',
        last_name='User',
    )


@pytest.fixture
def other_user(db):
    """Another user who owns a different startup"""
    return User.objects.create_user(
        email='other@example.com',
        password='testpass123',
        first_name='Other',
        last_name='User',
    )


@pytest.fixture
def startup(owner_user):
    """Startup owned by owner_user"""
    return StartupProfile.objects.create(
        user=owner_user,
        company_name='Test Startup',
        email='startup@example.com',
        description='Test startup description',
    )


@pytest.fixture
def other_startup(other_user):
    """Startup owned by other_user"""
    return StartupProfile.objects.create(
        user=other_user,
        company_name='Other Startup',
        email='other@example.com',
        description='Other startup description',
    )


@pytest.fixture
def public_project(startup):
    """Public project visible to everyone"""
    return Project.objects.create(
        startup=startup,
        title='Public Project',
        short_description='Public test project',
        description='Detailed description',
        status='idea',
        target_amount=Decimal('10000.00'),
        visibility='public',
    )


@pytest.fixture
def private_project(startup):
    """Private project visible only to owner"""
    return Project.objects.create(
        startup=startup,
        title='Private Project',
        short_description='Private test project',
        description='Detailed description',
        status='idea',
        target_amount=Decimal('5000.00'),
        visibility='private',
    )


@pytest.fixture
def unlisted_project(startup):
    """Unlisted project visible to authenticated users"""
    return Project.objects.create(
        startup=startup,
        title='Unlisted Project',
        short_description='Unlisted test project',
        description='Detailed description',
        status='idea',
        target_amount=Decimal('7500.00'),
        visibility='unlisted',
    )


@pytest.mark.django_db
class TestProjectCreatePermissions:
    """Test CREATE permissions - requires IsStartupOwner"""

    def test_owner_can_create_project(self, api_client, owner_user, startup):
        """Owner of startup can create projects"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/'
        data = {
            'title': 'New Project',
            'short_description': 'New project description',
            'target_amount': '15000.00',
            'status': 'idea',
            'visibility': 'public',
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Project'
        assert Project.objects.filter(startup=startup).count() == 1

    def test_non_owner_cannot_create_project(self, api_client, other_user, startup):
        """User who doesn't own startup cannot create projects"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/'
        data = {
            'title': 'Unauthorized Project',
            'short_description': 'Should fail',
            'target_amount': '10000.00',
            'status': 'idea',
            'visibility': 'public',
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Project.objects.filter(startup=startup).count() == 0

    def test_unauthenticated_cannot_create_project(self, api_client, startup):
        """Unauthenticated user cannot create projects"""
        url = f'/api/startups/{startup.id}/projects/'
        data = {
            'title': 'Anonymous Project',
            'short_description': 'Should fail',
            'target_amount': '10000.00',
            'status': 'idea',
            'visibility': 'public',
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
        assert Project.objects.filter(startup=startup).count() == 0


@pytest.mark.django_db
class TestProjectUpdatePermissions:
    """Test UPDATE permissions - requires IsOwnerOrReadOnly"""

    def test_owner_can_update_project(
        self, api_client, owner_user, startup, public_project
    ):
        """Owner can update their project"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        data = {'title': 'Updated Title', 'short_description': 'Updated description'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

        public_project.refresh_from_db()
        assert public_project.title == 'Updated Title'

    def test_non_owner_cannot_update_project(
        self, api_client, other_user, startup, public_project
    ):
        """Non-owner cannot update project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        data = {'title': 'Hacked Title'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

        public_project.refresh_from_db()
        assert public_project.title == 'Public Project'  # Unchanged

    def test_unauthenticated_cannot_update_project(
        self, api_client, startup, public_project
    ):
        """Unauthenticated user cannot update project"""
        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        data = {'title': 'Anonymous Update'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


@pytest.mark.django_db
class TestProjectDeletePermissions:
    """Test DELETE permissions - requires IsOwnerOrReadOnly"""

    def test_owner_can_delete_project(
        self, api_client, owner_user, startup, public_project
    ):
        """Owner can soft-delete their project"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        public_project.refresh_from_db()
        assert public_project.is_deleted is True
        assert public_project.deleted_by == owner_user

    def test_non_owner_cannot_delete_project(
        self, api_client, other_user, startup, public_project
    ):
        """Non-owner cannot delete project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        public_project.refresh_from_db()
        assert public_project.is_deleted is False

    def test_unauthenticated_cannot_delete_project(
        self, api_client, startup, public_project
    ):
        """Unauthenticated user cannot delete project"""
        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.delete(url)

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


@pytest.mark.django_db
class TestProjectVisibilityPermissions:
    """Test VIEW permissions based on visibility settings"""

    # PUBLIC PROJECTS
    def test_owner_can_view_public_project(
        self, api_client, owner_user, startup, public_project
    ):
        """Owner can view their public project"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Public Project'

    def test_authenticated_user_can_view_public_project(
        self, api_client, other_user, startup, public_project
    ):
        """Authenticated non-owner can view public project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Public Project'

    def test_unauthenticated_can_view_public_project(
        self, api_client, startup, public_project
    ):
        """Unauthenticated user can view public project"""
        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Public Project'

    # UNLISTED PROJECTS
    def test_owner_can_view_unlisted_project(
        self, api_client, owner_user, startup, unlisted_project
    ):
        """Owner can view their unlisted project"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{unlisted_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Unlisted Project'

    def test_authenticated_user_can_view_unlisted_project(
        self, api_client, other_user, startup, unlisted_project
    ):
        """Authenticated non-owner can view unlisted project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{unlisted_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Unlisted Project'

    def test_unauthenticated_cannot_view_unlisted_project(
        self, api_client, startup, unlisted_project
    ):
        """Unauthenticated user cannot view unlisted project"""
        url = f'/api/startups/{startup.id}/projects/{unlisted_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # PRIVATE PROJECTS
    def test_owner_can_view_private_project(
        self, api_client, owner_user, startup, private_project
    ):
        """Owner can view their private project"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{private_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Private Project'

    def test_authenticated_user_cannot_view_private_project(
        self, api_client, other_user, startup, private_project
    ):
        """Authenticated non-owner cannot view private project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{private_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_view_private_project(
        self, api_client, startup, private_project
    ):
        """Unauthenticated user cannot view private project"""
        url = f'/api/startups/{startup.id}/projects/{private_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProjectListVisibilityFiltering:
    """Test LIST endpoint filtering based on visibility"""

    def test_owner_sees_all_own_projects(
        self,
        api_client,
        owner_user,
        startup,
        public_project,
        private_project,
        unlisted_project,
    ):
        """Owner sees all their projects regardless of visibility"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_authenticated_user_sees_public_and_unlisted(
        self,
        api_client,
        other_user,
        startup,
        public_project,
        private_project,
        unlisted_project,
    ):
        """Authenticated non-owner sees only public and unlisted projects"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

        titles = [p['title'] for p in response.data['results']]
        assert 'Public Project' in titles
        assert 'Unlisted Project' in titles
        assert 'Private Project' not in titles

    def test_unauthenticated_sees_public_and_unlisted(
        self, api_client, startup, public_project, private_project, unlisted_project
    ):
        """Unauthenticated user sees only public and unlisted projects"""
        url = f'/api/startups/{startup.id}/projects/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

        titles = [p['title'] for p in response.data['results']]
        assert 'Public Project' in titles
        assert 'Unlisted Project' in titles
        assert 'Private Project' not in titles


@pytest.mark.django_db
class TestProjectStatusUpdatePermissions:
    """Test status update permissions"""

    def test_owner_can_update_status(
        self, api_client, owner_user, startup, public_project
    ):
        """Owner can update project status"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/status/'
        data = {'status': 'mvp'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'mvp'

    def test_non_owner_cannot_update_status(
        self, api_client, other_user, startup, public_project
    ):
        """Non-owner cannot update project status"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/status/'
        data = {'status': 'mvp'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_update_status(
        self, api_client, startup, public_project
    ):
        """Unauthenticated user cannot update project status"""
        url = f'/api/startups/{startup.id}/projects/{public_project.id}/status/'
        data = {'status': 'mvp'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


@pytest.mark.django_db
class TestPrivilegeEscalationAttempts:
    """Test attempts to escalate privileges or access unauthorized resources"""

    def test_cannot_create_project_for_another_startup(
        self, api_client, owner_user, other_startup
    ):
        """User cannot create project for startup they don't own"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{other_startup.id}/projects/'
        data = {
            'title': 'Escalation Attempt',
            'short_description': 'Should fail',
            'target_amount': '10000.00',
            'status': 'idea',
            'visibility': 'public',
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_change_project_ownership_via_update(
        self, api_client, owner_user, other_user, startup, other_startup, public_project
    ):
        """User cannot change project's startup via update"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/'
        # Attempt to change startup_id
        data = {'startup': other_startup.id, 'title': 'Stolen Project'}

        response = api_client.patch(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

        # Even if request succeeds, startup should not change
        public_project.refresh_from_db()
        assert public_project.startup == startup
        assert public_project.startup != other_startup

    def test_cannot_access_private_project_by_guessing_id(
        self, api_client, other_user, startup, private_project
    ):
        """User cannot access private project even if they know the ID"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{private_project.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAuditHistoryPermissions:
    """Test audit history access permissions"""

    def test_owner_can_view_audit_history(
        self, api_client, owner_user, startup, public_project
    ):
        """Owner can view audit history"""
        api_client.force_authenticate(user=owner_user)

        url = f'/api/startups/{startup.id}/projects/{public_project.id}/history/'
        response = api_client.get(url)

        # Should succeed (even if empty)
        assert response.status_code == status.HTTP_200_OK

    def test_non_owner_cannot_view_audit_history_of_private_project(
        self, api_client, other_user, startup, private_project
    ):
        """Non-owner cannot view audit history of private project"""
        api_client.force_authenticate(user=other_user)

        url = f'/api/startups/{startup.id}/projects/{private_project.id}/history/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
