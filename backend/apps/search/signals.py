import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from elasticsearch.exceptions import NotFoundError

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
        doc = ProjectDocument.search().query('match', id=str(project.id))
        results = doc.execute()
        if results.hits:
            results.hits[0].delete()
            logger.info(f'[SEARCH] Removed project {project.id} from index')
        else:
            logger.debug(
                f'[SEARCH] Project {project.id} not in index ('
                f'already deleted or never indexed)'
            )
    except NotFoundError:
        logger.debug(f'[SEARCH] Project {project.id} not found in index')
    except Exception as e:
        logger.error(
            f'[SEARCH] Failed to remove project {project.id}: {e}', exc_info=True
        )


@receiver(post_save, sender=Project)
def search_index_project_on_save(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'

    if instance.is_searchable:
        logger.info(
            f"[SEARCH] {action} project {instance.id} "
            f"'{instance.title}': indexing..."
        )
        index_project_in_search(instance)
    else:
        logger.info(
            f"[SEARCH] {action} project {instance.id}: " f"removing from index..."
        )
        remove_project_from_search(instance)


@receiver(post_delete, sender=Project)
def search_remove_project_on_delete(sender, instance, **kwargs):
    logger.info(
        f"[SEARCH] Deleted project {instance.id} '{instance.title}': "
        f"removing from index..."
    )
    remove_project_from_search(instance)
