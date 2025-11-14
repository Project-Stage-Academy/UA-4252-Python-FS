from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from apps.projects.models import Project
from apps.startups.models import StartupProfile


@registry.register_document
class StartupDocument(Document):
    tags = fields.KeywordField(multi=True)
    city = fields.KeywordField()

    class Index:
        name = "startups"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Django:
        model = StartupProfile
        fields = [
            "id",
            "company_name",
            "description",
            "email",
            "website",
            "address",
            "created_at",
            "updated_at",
        ]

    ignore_signals = False


@registry.register_document
class ProjectDocument(Document):
    tags = fields.KeywordField(multi=True)
    status = fields.KeywordField()

    class Index:
        name = "projects"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    class Django:
        model = Project
        fields = [
            "id",
            "title",
            "short_description",
            "description",
            "created_at",
            "updated_at",
        ]

    ignore_signals = False
