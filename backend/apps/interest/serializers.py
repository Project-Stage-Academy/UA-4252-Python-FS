from rest_framework import serializers
from .models import Interest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "project", "message", "contact_opt_in", "status"]
        read_only_fields = ["id", "status"]

    def validate(self, attrs):
        investor = self.context['request'].user
        project = attrs['project']

        if Interest.objects.filter(investor=investor, project=project).exists():
            raise serializers.ValidationError("Interest already expressed for this project.")

        return attrs

    def create(self, validated_data):
        investor = self.context['request'].user
        validated_data['investor'] = investor
        return super().create(validated_data)
