import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.projects.models import Project

from .documents import ProjectDocument

logger = logging.getLogger(__name__)


def index_project_in_search(project):
    """Helper: Index project in Elasticsearch."""
    try:
        doc = ProjectDocument()
        doc.update(project)
        logger.info(f"[SEARCH] Indexed project {project.id}")
    except Exception as e:
        logger.error(
            f"[SEARCH] Failed to index project {project.id}: {e}", exc_info=True
        )


def remove_project_from_search(project):
    """Helper: Remove project from Elasticsearch index."""
    try:
        ProjectDocument().get(id=str(project.id)).delete()
        logger.info(f"[SEARCH] Removed project {project.id} from index")
    except Exception as e:
        if 'NotFoundError' not in str(type(e).__name__):
            logger.error(f"[SEARCH] Failed to remove project {project.id}: {e}")


@receiver(post_save, sender=Project)
def search_index_project_on_save(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'

    if instance.is_searchable:
        logger.info(
            f"[SEARCH] {action} project {instance.id} '{instance.title}': indexing..."
        )
        index_project_in_search(instance)
    else:
        logger.info(f"[SEARCH] {action} project {instance.id}: removing from index...")
        remove_project_from_search(instance)


@receiver(post_delete, sender=Project)
def search_remove_project_on_delete(sender, instance, **kwargs):
    logger.info(
        f"[SEARCH] Deleted project {instance.id} '{instance.title}': "
        f"removing from index..."
    )
    remove_project_from_search(instance)
