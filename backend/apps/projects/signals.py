from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from .models import Project
from .tasks import send_project_notification
from apps.investors.models import SavedItem


def get_investors_by_saved_items(project: Project):
    project_ct = ContentType.objects.get_for_model(Project)
    startup_ct = ContentType.objects.get_for_model(project.startup.__class__)

    saved_project_investors = SavedItem.objects.filter(
        target_type=project_ct,
        target_id=project.id,
    ).values_list("investor_id", flat=True)

    saved_startup_investors = SavedItem.objects.filter(
        target_type=startup_ct,
        target_id=project.startup.id,
    ).values_list("investor_id", flat=True)

    return list(saved_project_investors | saved_startup_investors)


@receiver(post_save, sender=Project)
def project_created_handler(sender, instance, created, **kwargs):
    if created and instance.visibility == 'public':
        recipient_ids = get_investors_by_saved_items(instance)

        if recipient_ids:
            send_project_notification.delay(
                project_id=instance.id,
                notification_type='project_created',
                recipient_ids=recipient_ids
            )


@receiver(pre_save, sender=Project)
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Project.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Project.DoesNotExist:
            instance._old_status = None


@receiver(post_save, sender=Project)
def project_status_changed_handler(sender, instance, created, **kwargs):
    if created:
        return

    old_status = getattr(instance, '_old_status', None)

    if old_status and old_status != instance.status:
        recipient_ids = get_investors_by_saved_items(instance)

        if recipient_ids:
            if instance.status == Project.Status.FUNDRAISING:
                notification_type = 'status_changed_fundraising'
            elif instance.status == Project.Status.FUNDED:
                notification_type = 'status_changed_funded'
            else:
                notification_type = f'status_changed_{instance.status}'

            send_project_notification.delay(
                project_id=instance.id,
                notification_type=notification_type,
                recipient_ids=recipient_ids
            )
