from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from apps.investors.models import Tracking, SavedItem, ALLOWED_SAVED_MODELS
from apps.projects.models import Project
from apps.startups.models import StartupProfile


class TrackingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating (POST) a Tracking object.
    It validates target_id and automatically sets the investor.
    """
    investor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Tracking
        fields = [
            'id',
            'investor',
            'target_type',
            'target_id',
            'source',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        validators = []

    def validate(self, data):
        """
        We check whether the object we are trying to track exists.
        """
        target_type = data.get('target_type')
        target_id = data.get('target_id')

        if target_type == 'startup':
            if not StartupProfile.objects.filter(pk=target_id).exists():
                raise serializers.ValidationError(
                    {"target_id": "StartupProfile з таким 'target_id' не існує."}
                )
        elif target_type == 'project':
            if not Project.objects.filter(pk=target_id).exists():
                raise serializers.ValidationError(
                    {"target_id": "Project з таким 'target_id' не існує."}
                )
        else:
            raise serializers.ValidationError(
                {"target_type": "Неправильний 'target_type'."}
            )

        return data

    def create(self, validated_data):
        """
        Simple create. Idempotence (duplicate handling) is implemented in
        TrackingViewSet.create(), which catches IntegrityError and returns
        the existing record with HTTP 200.
        """
        return super().create(validated_data)


class TrackedStartupSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for StartupProfile as required by the task.
    """
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = StartupProfile
        fields = ['id', 'company_name', 'logo_url']

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo and hasattr(obj.logo, "url"):
            return request.build_absolute_uri(obj.logo.url)
        return None


class TrackedProjectSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for Project as required by the task.
    """

    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'thumbnail']


class TrackingListSerializer(serializers.ModelSerializer):
    """
    Serializer for a list (GET) of Tracking objects.
    The 'target' field will be added to the View for optimization.
    """
    target = serializers.JSONField(read_only=True, default=None)

    class Meta:
        model = Tracking
        fields = [
            'id',
            'created_at',
            'target_type',
            'target_id',
            'source',
            'target',
        ]


class SavedItemCreateSerializer(serializers.ModelSerializer):
    target_type = serializers.ChoiceField(
        choices=list(ALLOWED_SAVED_MODELS.keys()),
        write_only=True,
    )
    target_id = serializers.UUIDField()

    class Meta:
        model = SavedItem
        fields = ["id", "target_type", "target_id", "saved_at"]
        read_only_fields = ["id", "saved_at"]

    def validate(self, attrs):
        app_label, model_name = (ALLOWED_SAVED_MODELS[attrs.get("target_type")]
                                 .split("."))
        target_type = ContentType.objects.get(app_label=app_label, model=model_name)
        model_class = target_type.model_class()
        target_id = attrs.get("target_id")

        if not model_class.objects.filter(id=target_id).exists():
            raise serializers.ValidationError(
                {"target_id": "Object not found."}
            )

        attrs["target_type"] = target_type
        return attrs

    def create(self, validated_data):
        investor = validated_data.get("investor")

        if not investor:
            raise serializers.ValidationError(
                {"investor": "Investor must be provided."}
            )

        existing = SavedItem.objects.filter(
            investor=investor,
            target_type=validated_data["target_type"],
            target_id=validated_data["target_id"],
        ).first()

        if existing is not None:
            return existing

        return super().create(validated_data)
