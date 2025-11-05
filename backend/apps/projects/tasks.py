from celery import shared_task
from django.utils import timezone
from apps.user_messages.models import Notification

from .models import Project
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

        Notification.objects.bulk_create(notifications)

        return f'Created {len(notifications)} notifications for project {project_id}'

    except Project.DoesNotExist:
        raise self.retry(countdown=60)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)

@shared_task
def send_email_notification(notification_id):
    pass
