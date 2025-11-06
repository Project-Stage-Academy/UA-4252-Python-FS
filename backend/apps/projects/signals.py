from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Project
from .tasks import send_project_notification
from apps.startups.models import SavedStartup


@receiver(post_save, sender=Project)
def project_created_handler(sender, instance, created, **kwargs):
    if created and instance.visibility == 'public':
        saved_by = SavedStartup.objects.filter(
            startup=instance.startup
        ).values_list('investor_id', flat=True)

        recipient_ids = list(saved_by)

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
        saved_by = SavedStartup.objects.filter(
            startup=instance.startup
        ).value_list('investor_id', flat=True)

        recipient_ids = list(saved_by)

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
