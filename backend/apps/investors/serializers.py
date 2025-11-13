from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import SavedItem, ALLOWED_SAVED_MODELS


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
