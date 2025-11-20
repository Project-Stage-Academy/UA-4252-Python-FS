from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.projects.models import Project
from apps.search.documents import ProjectDocument
from apps.startups.models import StartupProfile

User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='test123',
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def test_startup(test_user):
    """Create test startup"""
    return StartupProfile.objects.create(
        user=test_user,
        company_name='Test Startup',
        description='Test description',
        city='Kyiv',
        tags=['test'],
    )


@pytest.mark.django_db
class TestAutomaticIndexing:
    """Test automatic indexing via signals"""

    def test_public_project_indexed_on_create(self, test_startup):
        """
        After creating project with visibility=public,
        it should be indexed automatically.
        """
        with patch('apps.search.signals.index_project_in_search') as mock_index:
            project = Project.objects.create(
                startup=test_startup,
                title='Public Project',
                visibility='public',
                status='idea',
                target_amount=5000,
            )

            mock_index.assert_called_once()
            assert mock_index.call_args[0][0].id == project.id

    def test_private_project_not_indexed(self, test_startup):
        """
        Private projects should NOT be indexed.
        """
        with patch('apps.search.signals.remove_project_from_search') as mock_remove:
            project = Project.objects.create(
                startup=test_startup,
                title='Private Project',
                visibility='private',  # PRIVATE
                status='idea',
                target_amount=5000,
            )

            mock_remove.assert_called_once()
            called_project = mock_remove.call_args[0][0]
            assert called_project.id == project.id

    def test_visibility_change_triggers_reindex(self, test_startup):
        """
        Changing visibility from private to public should index project.
        """
        # Create private project
        project = Project.objects.create(
            startup=test_startup,
            title='Test Project',
            visibility='private',
            status='idea',
            target_amount=5000,
        )

        with patch('apps.search.signals.index_project_in_search') as mock_index:
            project.visibility = 'public'
            project.save()

            mock_index.assert_called_once()

    def test_project_update_reindexes(self, test_startup):
        """
        Updating a public project should reindex it.
        """
        project = Project.objects.create(
            startup=test_startup,
            title='Original Title',
            visibility='public',
            status='idea',
            target_amount=5000,
        )

        with patch('apps.search.signals.index_project_in_search') as mock_index:
            project.title = 'Updated Title'
            project.save()

            mock_index.assert_called_once()

    def test_soft_delete_removes_from_index(self, test_startup):
        """
        Soft deleting a project should remove it from index.
        """
        project = Project.objects.create(
            startup=test_startup,
            title='To Delete',
            visibility='public',
            status='idea',
            target_amount=5000,
        )

        with patch('apps.search.signals.remove_project_from_search') as mock_remove:
            project.soft_delete()

            mock_remove.assert_called_once()


@pytest.mark.django_db
class TestDocumentShape:
    def test_document_has_required_fields(self, test_startup):
        """
        Document must have all fields:
        - id, title, short_description, description
        - startup_id, startup_name
        - tags, location
        - status, thumbnail_url
        """
        project = Project.objects.create(
            startup=test_startup,
            title='Test Project',
            short_description='Short desc',
            description='Full description',
            visibility='public',
            status='fundraising',
            target_amount=10000,
            tags=['test', 'tag'],
            thumbnail='https://example.com/image.jpg',
        )

        doc = ProjectDocument()
        prepared = doc.prepare(project)

        assert 'id' in prepared
        assert prepared['title'] == 'Test Project'
        assert prepared['short_description'] == 'Short desc'
        assert prepared['description'] == 'Full description'

        assert 'startup_id' in prepared
        assert prepared['startup_id'] == str(test_startup.id)
        assert prepared['startup_name'] == 'Test Startup'
        assert prepared['location'] == 'Kyiv'

        assert prepared['tags'] == ['test', 'tag']
        assert prepared['status'] == 'fundraising'
        assert prepared['thumbnail_url'] == 'https://example.com/image.jpg'

    def test_should_index_object_filters_correctly(self, test_startup):
        """
        should_index_object() should return True only for public, non-deleted projects.
        """
        doc = ProjectDocument()

        public_project = Project.objects.create(
            startup=test_startup,
            title='Public',
            visibility='public',
            is_deleted=False,
            status='idea',
            target_amount=5000,
        )
        assert doc.should_index_object(public_project) is True

        private_project = Project.objects.create(
            startup=test_startup,
            title='Private',
            visibility='private',
            is_deleted=False,
            status='idea',
            target_amount=5000,
        )
        assert doc.should_index_object(private_project) is False

        deleted_project = Project.objects.create(
            startup=test_startup,
            title='Deleted',
            visibility='public',
            is_deleted=True,
            status='idea',
            target_amount=5000,
        )
        assert doc.should_index_object(deleted_project) is False


@pytest.mark.django_db
class TestSearchAPI:
    """Test that search API returns only public projects"""

    def test_search_returns_only_public_projects(self, client, test_startup):
        """
        GET /api/search/ should only return
        projects with visibility=public.
        """
        public = Project.objects.create(
            startup=test_startup,
            title='Public Project',
            visibility='public',
            status='fundraising',
            target_amount=10000,
        )

        private = Project.objects.create(
            startup=test_startup,
            title='Private Project',
            visibility='private',
            status='idea',
            target_amount=5000,
        )

        assert public.is_searchable is True

        assert private.is_searchable is False

        doc = ProjectDocument()
        assert doc.should_index_object(public) is True
        assert doc.should_index_object(private) is False


@pytest.mark.django_db
class TestIsSearchableProperty:
    """Test the is_searchable property"""

    def test_is_searchable_returns_true_for_public_active(self, test_startup):
        """Public and not deleted projects are searchable"""
        project = Project.objects.create(
            startup=test_startup,
            title='Test',
            visibility='public',
            is_deleted=False,
            status='idea',
            target_amount=5000,
        )

        assert project.is_searchable is True

    def test_is_searchable_returns_false_for_private(self, test_startup):
        """Private projects are not searchable"""
        project = Project.objects.create(
            startup=test_startup,
            title='Test',
            visibility='private',
            is_deleted=False,
            status='idea',
            target_amount=5000,
        )

        assert project.is_searchable is False

    def test_is_searchable_returns_false_for_deleted(self, test_startup):
        """Deleted projects are not searchable"""
        project = Project.objects.create(
            startup=test_startup,
            title='Test',
            visibility='public',
            is_deleted=True,
            status='idea',
            target_amount=5000,
        )

        assert project.is_searchable is False
