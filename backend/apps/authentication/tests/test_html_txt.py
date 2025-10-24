# from django.test import SimpleTestCase  # <-- CHANGE THIS
from django.test import TestCase # <-- USE THIS INSTEAD
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from ..emails import send_password_reset_email

User = get_user_model()

# Change inheritance to TestCase to allow database access
class PasswordResetEmailTemplateTest(TestCase): 
    """Юніт-тести для шаблону password_reset_email.html"""

    def setUp(self):
        # When using TestCase, it's best to create the user in setUp if you need it in multiple tests
        # Note: We must use objects.create() here because TestCase uses the database
        self.user = User.objects.create(first_name='Roman', email='roman@example.com') 
        self.context = {
            'user': self.user,
            'reset_link': 'http://example.com/reset/abc123/',
            'expiry_minutes': 30
        }

    TEMPLATE_PATH = 'authentication/password_reset_request.html'


    def test_template_renders_with_context(self):
        """Перевіряє, що шаблон рендериться і містить усі змінні контексту"""
        html = render_to_string(self.TEMPLATE_PATH, self.context)
        self.assertIn('Hello, Roman', html)
        self.assertIn('To update your password', html)
        self.assertIn('http://example.com/reset/abc123/', html)
        self.assertIn('30', html)
        self.assertIn('ignore this email', html)

    def test_template_has_html_tags(self):
        """Перевіряє, що шаблон має базову HTML-структуру"""
        html = render_to_string(self.TEMPLATE_PATH, self.context)
        self.assertIn('<div', html)
        self.assertIn('</div>', html)
        self.assertIn('<a href="http://example.com/reset/abc123/">', html)

    def test_template_title_block(self):
        """Перевіряє наявність блоку title (або тексту, що його імітує)"""
        html = render_to_string(self.TEMPLATE_PATH, self.context)
        self.assertIn('Password Reset Request', html)

    def test_send_password_reset_email_without_email(self):
        user_no_email = User.objects.create(first_name='NoEmailUser', email='')
        with self.assertRaises(ValueError):
             send_password_reset_email(user_no_email, "http://example.com/reset")