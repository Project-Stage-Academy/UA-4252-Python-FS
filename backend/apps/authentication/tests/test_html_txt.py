from django.test import SimpleTestCase
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetEmailTemplateTest(SimpleTestCase):
    """Юніт-тести для шаблону password_reset_email.html"""

    def setUp(self):
        self.user = User(first_name='Roman', email='roman@example.com') 
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
        self.assertIn('reset your password', html)
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
