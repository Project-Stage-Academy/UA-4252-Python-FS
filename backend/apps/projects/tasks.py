from celery import shared_task

from .models import Project
from apps.user_messages.models import Notification
from .emails import send_project_notification_email
from django.conf import settings


@shared_task(bind=True, max_retries=5)
def send_project_notification(self, project_id, notification_type, recipient_ids):
    """    Create notification entries for interested users. """
    try:
        project = Project.objects.get(id=project_id)
        messages = {
            'project_created': {
                'title': f'New Project: {project.title}',
                'message': f'{project.startup.company_name} has launched a new project.'
            },
            'status_changed_fundraising': {
                'title': f'Fundraising Started: {project.title}',
                'message': f'{project.title} is now raising funds!',
            },
            'status_changed_funded': {
                'title': f'Project Funded: {project.title}',
                'message': f'{project.title} has successfully reached its funding goal!'
            },
        }

        notification_data = messages.get(notification_type, {
            'title': f'Update: {project.title}',
            'message': f'{project.title} has been update. '
        })

        notifications = []
        for recipient_id in recipient_ids:
            notification = Notification(
                user_id=recipient_id,
                notification_type=notification_type,
                title=notification_data['title'],
                message=notification_data['message'],
                link_url=f'/projects/{project.slug}/',
                related_project=project,
            )
            notifications.append(notification)

        created_notifications = Notification.objects.bulk_create(
            notifications,
            update_conflicts=False
        )
        notification_ids = [n.id for n in created_notifications]

        for notification_id in notification_ids:
            send_notification_email_task.delay(notification_id)

        return f'Created {len(notifications)} notifications for project {project_id}'

    except Project.DoesNotExist:
        raise self.retry(countdown=60)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@shared_task
def send_notification_email_task(notification_id):
    try:
        notification = Notification.objects.select_related(
            'related_project',
            'related_project__startup',
            'user'
        ).get(id=notification_id)

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        project_url = f'{frontend_url}/projects/{notification.related_project.slug}/'

        send_project_notification_email(notification, project_url)

        return f'Email sent for notification {notification_id}'

    except Notification.DoesNotExist:
        return f'Notification {notification_id} not found'
    except Exception:
        raise
