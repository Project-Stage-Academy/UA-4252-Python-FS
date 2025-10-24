"""Module for generating and sending emails"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(user, reset_link: str) -> None:
    subject = 'Password Reset Request'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@siskidomain.com')
    recipient_list = [user.email]

    context = {
        'user': user,
        'reset_link': reset_link,
    }

    html_email = render_to_string('authentication/password_reset_request.html', context)
    text_email = render_to_string('authentication/password_reset_request.txt', context)

    email = EmailMultiAlternatives(subject, text_email, from_email, recipient_list)
    email.attach_alternative(html_email, 'text/html')

    try:
        email.send(fail_silently=False)
    except Exception as e:
        logger.error(f'Email sending failed for user {user.email}: {e}')
