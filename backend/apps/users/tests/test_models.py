from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class UserModelTests(TestCase):
    """Class for testing custom User model."""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password123'
        }

    def test_create_user_successful(self):
        """Test create user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_user_id_is_uuid(self):
        """Test user id is UUID"""
        user = User.objects.create_user(**self.user_data)
        self.assertIsInstance(user.id, uuid.UUID)

    def test_create_user_without_email_raises_error(self):
        """Test user without email raises ValueError"""
        data = self.user_data.copy()
        data['email'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)

    def test_create_user_without_first_name_raises_error(self):
        """Test user without first name raises ValueError"""
        data = self.user_data.copy()
        data['first_name'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)

    def test_create_user_without_last_name_raises_error(self):
        """Test user without last name raises ValueError"""
        data = self.user_data.copy()
        data['last_name'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)

    def test_create_user_with_existing_email_raises_error(self):
        """Test create_user raises IntegrityError if email already exists"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_change_email_to_existing_email_raises_error(self):
        """Test user cannot change email to an existing email"""
        user1 = User.objects.create_user(**self.user_data)

        data = self.user_data.copy()
        data['email'] = 'another_email@example.com'
        user2 = User.objects.create_user(**data)

        with self.assertRaises(IntegrityError):
            user2.email = user1.email
            user2.save()

    def test_new_user_email_normalized(self):
        """Test emails are normalized"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        data = self.user_data.copy()
        data.pop('email')
        for email, expected in sample_emails:
            user = User.objects.create_user(**data, email=email)
            self.assertEqual(user.email, expected)

    def test_create_superuser_successful(self):
        """Test create superuser"""
        superuser = User.objects.create_superuser(**self.user_data)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_superuser_with_invalid_flags_raises_error(self):
        """
        Test create superuser without is_staff
        or is_superuser=True raises ValueError
        """
        data = self.user_data.copy()
        data['is_staff'] = False
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**data)

        data = self.user_data.copy()
        data['is_superuser'] = False
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**data)

    def test_str_returns_email(self):
        """Test __str__ method returns email"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
