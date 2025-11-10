import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_project_notification_email(notification, project_url):
    project = notification.related_project
    if not project:
        logger.error(f'No project associated with notification {notification.id}')
        return

    startup = project.startup
    recipient_email = notification.user.email

    if not recipient_email:
        logger.error(f'No email for user {notification.user.id}')
        return

    template_map = {
        'project_created': 'project_created',
        'status_changed_fundraising': 'project_fundraising',
        'status_changed_funded': 'project_funded',
    }

    template_name = template_map.get(
        notification.notification_type,
        'project_created'
    )

    subject_map = {
        'project_created': f'New Project: {project.title}',
        'status_changed_fundraising': f'Fundraising Started: {project.title}',
        'status_changed_funded': f'Project Funded: {project.title}',
    }

    subject = subject_map.get(
        notification.notification_type,
        f'Project Update: {project.title}'
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@siskidomain.com")

    context = {
        'project': project,
        'startup': startup,
        'project_url': project_url,
    }

    try:
        html_email = render_to_string(
            f'projects/{template_name}.html', context)
        text_email = render_to_string(
            f'projects/{template_name}.txt', context)

        email = EmailMultiAlternatives(
            subject,
            text_email,
            from_email,
            [recipient_email],
        )
        email.attach_alternative(html_email, "text/html")
        email.send(fail_silently=False)

        logger.info(
            f'Email sent to {recipient_email} for notification {notification.id}'
        )

    except Exception as e:
        logger.error(f'Email sending failed for {recipient_email}: {e}')
        raise
