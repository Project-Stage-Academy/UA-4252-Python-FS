from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry


class Command(BaseCommand):
    """
    Django command to check Elasticsearch indices, registered
    using django-elasticsearch-dsl Documents.
    If index already exists:
        - skip.
    If index DOES NOT EXIST:
        - create index;
        - populate created index with initial data.
    Does not detect changes in index structure.
    """

    def handle(self, *args, **options):
        self.stdout.write("Checking Elasticsearch indices...")

        for document in registry.get_documents():
            index = document._index

            if index.exists():
                continue

            self.stdout.write(f"Creating index '{index._name}'...")
            index.create()

            doc = document()
            self.stdout.write(f"Populating index '{index._name}' with "
                              f"{doc.get_queryset().count()} objects...")
            qs = doc.get_indexing_queryset()
            doc.update(qs)

        self.stdout.write(self.style.SUCCESS("Indices check complete"))
