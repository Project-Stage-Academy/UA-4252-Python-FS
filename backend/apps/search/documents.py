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
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

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
    visibility = fields.KeywordField()
    thumbnail_url = fields.TextField()

    startup_id = fields.KeywordField()
    startup_name = fields.TextField(
        attr='startup.company_name', fields={'raw': fields.KeywordField()}
    )
    location = fields.KeywordField()

    class Index:
        name = "projects"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

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
        related_models = [StartupProfile]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, StartupProfile):
            return related_instance.projects.all()
        return []

    def prepare_startup_id(self, instance):
        return str(instance.startup.id)

    def prepare_startup_name(self, instance):
        return instance.startup.company_name

    def prepare_location(self, instance):
        return instance.startup.city or ''

    def prepare_thumbnail_url(self, instance):
        return instance.thumbnail_url or ''

    def should_index_object(self, instance):
        return instance.is_searchable

    ignore_signals = False
