from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django_fsm import TransitionNotAllowed

from apps.projects.models import Project
from apps.startups.models import StartupProfile

User = get_user_model()


class StatusTransitionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassw',
            first_name='Test',
            last_name='User',
        )
        self.startup = StartupProfile.objects.create(
            user=self.user, company_name='Test Startup'
        )
        self.project = Project.objects.create(
            startup=self.startup,
            title='Test Project',
            target_amount=Decimal('10000.00'),
        )

    def test_valid_transition_idea_to_mvp(self):
        self.assertEqual(self.project.status, Project.Status.IDEA)
        self.project.start_mvp()
        self.project.save()
        self.assertEqual(self.project.status, Project.Status.MVP)

    def test_valid_transition_mvp_to_fundraising(self):
        self.project.start_mvp()
        self.project.save()
        self.project.start_fundraising()
        self.project.save()
        self.assertEqual(self.project.status, Project.Status.FUNDRAISING)

    def test_invalid_transition_idea_to_funded(self):
        with self.assertRaises(TransitionNotAllowed):
            self.project.mark_funded()

    def test_auto_funding_when_target_reached(self):
        self.project.start_mvp()
        self.project.start_fundraising()
        self.project.save()

        self.project.raised_amount = 10000
        self.project.save()

        result = self.project.check_auto_funding()
        self.assertTrue(result)
        self.assertEqual(self.project.status, Project.Status.FUNDED)
        self.assertIsNotNone(self.project.funded_at)

    def test_overfunding_blocked_by_default(self):
        self.project.raised_amount = 15000
        with self.assertRaises(ValidationError):
            self.project.full_clean()

    def test_overfunding_allowed_with_flag(self):
        self.project.allow_overfunding = True
        self.project.raised_amount = 15000
        self.project.full_clean()

    def test_funded_at_recorded(self):
        self.project.start_mvp()
        self.project.start_fundraising()
        self.project.save()

        self.assertIsNone(self.project.funded_at)

        self.project.mark_funded()
        self.project.save()

        self.assertIsNotNone(self.project.funded_at)
