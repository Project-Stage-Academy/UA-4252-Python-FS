from rest_framework import serializers
from .models import Project


class ProjectReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'status',
            'thumbnail',
            'short_description'
        ]


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'startup',
            'title',
            'slug',
            'short_description',
            'description',
            'status',
            'target_amount',
            'raised_amount',
            'currency',
            'thumbnail',
            'tags',
            'visibility'
        ]
        read_only_fields = ['startup', 'raised_amount']

    def validate_target_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Target amount cannot be negative.")
        return value

    def validate_raised_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Raised amount cannot be negative.")
        return value
