from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project, ProjectAudit
from apps.startups.models import StartupProfile

User = get_user_model()


class ProjectAuditTestCase(TestCase):
    """Test cases for Project audit logging"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            first_name='Owner',
            last_name='User',
            password='testpass123',
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='Person',
            password='testpass123',
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='startup@example.com',
            description='Test description',
            phone='+380501234567',
            city='Kyiv',
        )

        self.client = APIClient()

    def test_audit_log_created_on_project_create(self):
        initial_count = ProjectAudit.objects.count()
        self.assertEqual(initial_count, 0)

        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Short desc',
            description='Full description',
            target_amount=Decimal('100000.00'),
            currency='UAH',
            visibility='public',
        )

        audit_logs = ProjectAudit.objects.filter(project=project)
        self.assertEqual(audit_logs.count(), 1)

        log = audit_logs.first()
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.project, project)
        self.assertIsNone(log.user)  # User не передано
        self.assertIsNotNone(log.timestamp)

        self.assertIn('before', log.changes)
        self.assertIn('after', log.changes)
        self.assertEqual(log.changes['before'], {})  # До створення нічого не було
        self.assertIn('title', log.changes['after'])
        self.assertEqual(log.changes['after']['title'], 'Test Project')

    def test_audit_log_created_on_project_update(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Original Title',
            short_description='Original desc',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        initial_audit_count = ProjectAudit.objects.filter(project=project).count()

        project.title = 'Updated Title'
        project.target_amount = Decimal('150000.00')
        project.save()

        audit_logs = ProjectAudit.objects.filter(project=project)
        self.assertEqual(audit_logs.count(), initial_audit_count + 1)

        update_log = audit_logs.filter(action='update').first()
        self.assertIsNotNone(update_log)

        changes = update_log.changes
        self.assertIn('before', changes)
        self.assertIn('after', changes)
        self.assertIn('changed_fields', changes)

        self.assertEqual(changes['before']['title'], 'Original Title')
        self.assertEqual(changes['after']['title'], 'Updated Title')
        self.assertEqual(changes['before']['target_amount'], 100000.0)
        self.assertEqual(changes['after']['target_amount'], 150000.0)

        self.assertIn('title', changes['changed_fields'])
        self.assertIn('target_amount', changes['changed_fields'])

    def test_audit_log_excludes_auto_updated_fields(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )
        project.title = 'Updated Title'
        project.save()

        update_log = ProjectAudit.objects.filter(
            project=project, action='update'
        ).first()

        self.assertIsNotNone(update_log)

        changed_fields = update_log.changes.get('changed_fields', [])
        self.assertNotIn('updated_at', changed_fields)
        self.assertNotIn('created_at', changed_fields)
        self.assertNotIn('id', changed_fields)

        self.assertIn('title', changed_fields)

    def test_audit_log_multiple_updates(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Original',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        project.title = 'Update 1'
        project.save()

        project.target_amount = Decimal('150000.00')
        project.save()

        project.visibility = 'private'
        project.save()

        audit_logs = ProjectAudit.objects.filter(project=project)
        self.assertEqual(audit_logs.count(), 4)

        create_logs = audit_logs.filter(action='create')
        update_logs = audit_logs.filter(action='update')

        self.assertEqual(create_logs.count(), 1)
        self.assertEqual(update_logs.count(), 3)

    def test_audit_log_on_soft_delete(self):
        """Тест: audit log with soft delete"""
        project = Project.objects.create(
            startup=self.startup,
            title='To Delete',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        initial_count = ProjectAudit.objects.filter(project=project).count()

        # Soft delete
        project.soft_delete(user=self.user)

        audit_logs = ProjectAudit.objects.filter(project=project)
        self.assertGreater(audit_logs.count(), initial_count)

        delete_log = None
        for log in audit_logs.filter(action='update'):
            if 'is_deleted' in log.changes.get('changed_fields', []):
                delete_log = log
                break

        self.assertIsNotNone(delete_log)
        self.assertTrue(delete_log.changes['after']['is_deleted'])

    def test_audit_log_with_user_attribution(self):
        """Тест: audit log"""
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        project.title = 'Updated by User'
        project._audit_user = self.user
        project.save()

        update_log = ProjectAudit.objects.filter(
            project=project, action='update'
        ).first()

        self.assertIsNotNone(update_log)
        self.assertEqual(update_log.user, self.user)

    def test_audit_log_excludes_technical_fields(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        project.title = 'Updated'
        project.save()

        update_log = ProjectAudit.objects.filter(
            project=project, action='update'
        ).first()

        changed_fields = update_log.changes.get('changed_fields', [])

        self.assertNotIn('id', changed_fields)
        self.assertNotIn('created_at', changed_fields)
        self.assertNotIn('updated_at', changed_fields)
        self.assertNotIn('_state', changed_fields)


class ProjectHistoryAPITestCase(TestCase):
    """Test cases for Project History API endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            first_name='Owner',
            last_name='User',
            password='testpass123',
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='startup@example.com',
            description='Test description',
            phone='+380501234567',
            city='Kyiv',
        )

        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Short',
            description='Full',
            target_amount=Decimal('100000.00'),
            currency='UAH',
            visibility='public',
        )

        # Створюємо кілька оновлень для історії
        self.project.title = 'Updated Title 1'
        self.project.save()

        self.project.target_amount = Decimal('150000.00')
        self.project.save()

        self.project.visibility = 'private'
        self.project.save()

        self.client = APIClient()
        self.history_url = (
            f'/api/startups/{self.startup.pk}/projects/{self.project.pk}/history/'
        )

    def test_history_endpoint_exists(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_returns_audit_logs(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(len(response.data['results']), 0)

        first_log = response.data['results'][0]
        self.assertIn('id', first_log)
        self.assertIn('action', first_log)
        self.assertIn('timestamp', first_log)
        self.assertIn('changes', first_log)
        self.assertIn('user_name', first_log)
        self.assertIn('changed_fields_display', first_log)

    def test_history_pagination_works(self):
        self.client.force_authenticate(user=self.user)

        # Запит з page_size=2
        response = self.client.get(self.history_url, {'page_size': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        self.assertLessEqual(len(response.data['results']), 2)

    def test_history_filter_by_action_update(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url, {'action': 'update'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for log in response.data['results']:
            self.assertEqual(log['action'], 'update')

    def test_history_filter_by_action_create(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url, {'action': 'create'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertGreater(len(response.data['results']), 0)

        for log in response.data['results']:
            self.assertEqual(log['action'], 'create')

    def test_history_ordered_by_timestamp_desc(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        if len(results) > 1:
            timestamps = [log['timestamp'] for log in results]
            self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_history_shows_user_name(self):
        self.project.title = 'Updated by User'
        self.project._audit_user = self.user
        self.project.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_log = None
        system_log = None

        for log in response.data['results']:
            if log['user_email'] == self.user.email:
                user_log = log
            elif log['user_email'] is None:
                system_log = log

        if user_log:
            self.assertIn('Owner', user_log['user_name'])

        if system_log:
            self.assertEqual(system_log['user_name'], 'System')

    def test_history_changed_fields_display(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.history_url, {'action': 'update'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if len(response.data['results']) > 0:
            log = response.data['results'][0]
            changed_fields = log['changed_fields_display']

            self.assertIsInstance(changed_fields, list)

            if changed_fields:
                self.assertIsInstance(changed_fields[0], str)
                for field in changed_fields:
                    self.assertNotIn('_', field.lower().replace(' ', ''))

    def test_history_unauthorized_access(self):
        self.project.visibility = 'private'
        self.project.save()

        response = self.client.get(self.history_url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_history_forbidden_for_non_owner(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            first_name='Other',
            last_name='User',
            password='testpass123',
        )

        self.project.visibility = 'private'
        self.project.save()

        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.history_url)

        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )


class AuditSerializationTestCase(TestCase):
    """Test cases for audit value serialization"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
        )

        self.startup = StartupProfile.objects.create(
            user=self.user,
            company_name='Test Startup',
            email='startup@example.com',
            phone='+380501234567',
            city='Kyiv',
        )

    def test_decimal_serialization(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test',
            target_amount=Decimal('123456.78'),
            currency='UAH',
        )

        log = ProjectAudit.objects.filter(project=project, action='create').first()

        target_amount = log.changes['after']['target_amount']
        self.assertIsInstance(target_amount, float)
        self.assertEqual(target_amount, 123456.78)

    def test_datetime_serialization(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test',
            target_amount=Decimal('100000.00'),
            currency='UAH',
        )

        project.funded_at = timezone.now()
        project.save()

        log = ProjectAudit.objects.filter(project=project, action='update').first()

        funded_at = log.changes['after'].get('funded_at')
        if funded_at:
            self.assertIsInstance(funded_at, str)
            self.assertRegex(funded_at, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

    def test_array_field_serialization(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test',
            target_amount=Decimal('100000.00'),
            currency='UAH',
            tags=['tech', 'innovation', 'AI'],
        )

        log = ProjectAudit.objects.filter(project=project, action='create').first()

        tags = log.changes['after']['tags']
        self.assertIsInstance(tags, list)
        self.assertEqual(tags, ['tech', 'innovation', 'AI'])
