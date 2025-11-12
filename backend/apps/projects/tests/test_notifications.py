from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.projects.models import Project
from apps.startups.models import StartupProfile
from apps.investors.models import InvestorProfile, SavedItem
from apps.user_messages.models import Notification
from apps.projects.tasks import send_project_notification

User = get_user_model()


class ProjectNotificationTestCase(TestCase):

    def setUp(self):
        self.startup_user = User.objects.create_user(
            email='startup@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Startup'
        )
        self.investor_user = User.objects.create_user(
            email='investor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Investor'
        )
        self.startup = StartupProfile.objects.create(
            user=self.startup_user,
            company_name='Test Startup',
            email='startup@test.com'
        )
        self.investor = InvestorProfile.objects.create(
            user=self.investor_user,
            company_name='Test Investor',
            email='investor@test.ua',
            investment_range_min=10000,
            investment_range_max=100000
        )
        SavedItem.objects.create(
            investor=self.investor,
            target_object=self.startup,
        )

    @patch('apps.projects.tasks.send_notification_email_task.delay')
    @patch('apps.projects.signals.send_project_notification.delay')
    def test_project_created_notification(self, mock_notification_task,
                                          mock_email_task):
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Test description',
            status=Project.Status.IDEA,
            target_amount=50000,
            visibility='public'
        )

        mock_notification_task.assert_called_once()
        call_args = mock_notification_task.call_args[1]

        self.assertEqual(call_args['project_id'], project.id)
        self.assertEqual(call_args['notification_type'], 'project_created')
        self.assertIn(self.investor.id, call_args['recipient_ids'])

    @patch('apps.projects.tasks.send_notification_email_task.delay')
    @patch('apps.projects.signals.send_project_notification.delay')
    def test_private_project_no_notification(self, mock_notification_task,
                                             mock_email_task):
        Project.objects.create(
            startup=self.startup,
            title='Private Project',
            short_description='Test description',
            status=Project.Status.IDEA,
            target_amount=50000,
            visibility='private'
        )
        mock_notification_task.assert_not_called()

    @patch('apps.projects.tasks.send_notification_email_task.delay')
    @patch('apps.projects.signals.send_project_notification.delay')
    def test_status_change_to_fundraising_notification(self, mock_notification_task,
                                                       mock_email_task):
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Test description',
            status=Project.Status.IDEA,
            target_amount=50000,
            visibility='public'
        )

        mock_notification_task.reset_mock()

        project.start_mvp()
        project.save()

        mock_notification_task.reset_mock()

        project.start_fundraising()
        project.save()

        mock_notification_task.assert_called_once()
        call_args = mock_notification_task.call_args[1]

        self.assertEqual(call_args['project_id'], project.id)
        self.assertEqual(call_args['notification_type'], 'status_changed_fundraising')
        self.assertIn(self.investor.id, call_args['recipient_ids'])

    @patch('apps.projects.tasks.send_notification_email_task.delay')
    @patch('apps.projects.signals.send_project_notification.delay')
    def test_status_change_to_funded_notification(self, mock_notification_task,
                                                  mock_email_task):
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Test description',
            status=Project.Status.FUNDRAISING,
            target_amount=50000,
            raised_amount=50000,
            visibility='public'
        )

        mock_notification_task.reset_mock()

        project.mark_funded()
        project.save()

        mock_notification_task.assert_called_once()
        call_args = mock_notification_task.call_args[1]

        self.assertEqual(call_args['project_id'], project.id)
        self.assertEqual(call_args['notification_type'], 'status_changed_funded')
        self.assertIn(self.investor.id, call_args['recipient_ids'])

    def test_notification_created_in_database(self):
        project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            short_description='Test description',
            status=Project.Status.IDEA,
            target_amount=50000,
            visibility='public'
        )

        send_project_notification.apply(
            kwargs={
                'project_id': project.id,
                'notification_type': 'project_created',
                'recipient_ids': [self.investor.id]
            }
        )

        notification = Notification.objects.filter(
            user=self.investor,
            related_project=project,
            notification_type='project_created'
        ).first()

        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, f'New Project: {project.title}')
        self.assertFalse(notification.is_read)
