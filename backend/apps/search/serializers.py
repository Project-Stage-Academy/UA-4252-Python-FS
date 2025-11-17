from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from .documents import ProjectDocument, StartupDocument


class ElasticSearchSerializer(DocumentSerializer):
    score = serializers.FloatField(source="meta.score")
    highlight = serializers.JSONField(source="meta.highlight.to_dict", default={})

    class Meta:
        abstract = True


class StartupDocumentSerializer(ElasticSearchSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        document = StartupDocument
        fields = [
            "id",
            "type",
            "company_name",
            "description",
            "email",
            "website",
            "city",
            "address",
            "tags",
            "created_at",
            "updated_at",
        ]

    def get_type(self, obj):
        return "startup"


class ProjectDocumentSerializer(ElasticSearchSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        document = ProjectDocument
        fields = [
            "id",
            "type",
            "title",
            "short_description",
            "description",
            "status",
            "tags",
            "created_at",
            "updated_at",
            "visibility",
            "startup_id",
            "startup_name",
            "location",
            "thumbnail_url",
        ]

    def get_type(self, obj):
        return "project"
