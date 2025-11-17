from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Project, ProjectAudit
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

User = get_user_model()


def create_audit_log(project, action, changes, user=None, request=None):
    user_agent = ''
    if request:
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    ProjectAudit.objects.create(
        project=project,
        user=user,
        action=action,
        changes=changes,
        user_agent=user_agent,
    )


def get_field_diff(old_instance, new_instance, exclude_field=None):
    if exclude_field is None:
        exclude_field = [
            'id',
            'created_at',
            'updated_at',
            '_old_status',
            '_old_instance',
            '_state',
            '_audit_user',
            '_audit_request',
        ]
    before = {}
    after = {}
    changed_fields = []

    for field in new_instance._meta.fields:
        field_name = field.name
        if field_name in exclude_field:
            continue

        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)

        old_value = _serialize_value(old_value)
        new_value = _serialize_value(new_value)

        if old_value != new_value:
            before[field_name] = old_value
            after[field_name] = new_value
            changed_fields.append(field_name)

    return {'before': before, 'after': after, 'changed_fields': changed_fields}


def _serialize_value(value):
    if value is None:
        return None
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, User):
        return str(value.id)
    elif hasattr(value, 'id'):
        return str(value.id)
    elif isinstance(value, list):
        return value
    else:
        return str(value)


@receiver(post_save, sender=Project)
def project_created_handler(sender, instance, created, **kwargs):
    if created and instance.visibility == 'public':
        recipient_ids = get_investors_by_saved_items(instance)

        if recipient_ids:
            send_project_notification.delay(
                project_id=instance.id,
                notification_type='project_created',
                recipient_ids=recipient_ids,
            )


@receiver(pre_save, sender=Project)
def store_old_instance(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Project.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_instance = old_instance
        except Project.DoesNotExist:
            instance._old_status = None
            instance._old_instance = None


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
                recipient_ids=recipient_ids,
            )


@receiver(post_save, sender=Project)
def create_audit_log_on_save(sender, instance, created, **kwargs):
    user = getattr(instance, '_audit_user', None)
    request = getattr(instance, '_audit_request', None)

    if created:
        changes = {
            'before': {},
            'after': {
                field.name: _serialize_value(getattr(instance, field.name))
                for field in instance._meta.fields
                if field.name not in ['id', 'created_at', 'updated_at']
            },
            'changed_fields': [],
        }
        create_audit_log(instance, 'create', changes, user, request)
    else:
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            changes = get_field_diff(old_instance, instance)
            if changes['changed_fields']:
                create_audit_log(instance, 'update', changes, user, request)


@receiver(post_delete, sender=Project)
def create_audit_log_delete(sender, instance, **kwargs):
    user = getattr(instance, '_audit_user', None)
    request = getattr(instance, '_audit_request', None)

    changes = {
        'before': {
            field.name: _serialize_value(getattr(instance, field.name))
            for field in instance._meta.fields
            if field.name not in ['id', 'created_at', 'updated_at']
        },
        'after': {},
        'changed_fields': [],
    }

    create_audit_log(instance, 'delete', changes, user, request)
