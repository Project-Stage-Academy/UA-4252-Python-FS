"""Module for generating and sending emails"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(user, reset_link: str) -> None:
    subject = 'Password Reset Request'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@siskidomain.com')
    reply_to_email = getattr(settings, 'EMAIL_REPLY_TO', 'support@yourdomain.com')
    expiry_minutes = settings.PASSWORD_RESET_TIMEOUT // 60

    if not getattr(user, 'email', None):
        logger.error(f"⚠️ Password reset requested for user without valid email: {user}")
        raise ValueError("User has no valid email address.")

    recipient_list = [user.email]

    context = {
        'user': user,
        'reset_link': reset_link,
        'expiry_minutes': expiry_minutes,
    }

    html_email = render_to_string('authentication/password_reset_request.html', context)
    text_email = render_to_string('authentication/password_reset_request.txt', context)

    email = EmailMultiAlternatives(
        subject, 
        text_email, 
        from_email, 
        recipient_list, 
        reply_to=[reply_to_email]
    )
    email.attach_alternative(html_email, 'text/html')

    try:
        email.send(fail_silently=False)
    except Exception as e:
        logger.error(f'Email sending failed for user {user.email}: {e}')
