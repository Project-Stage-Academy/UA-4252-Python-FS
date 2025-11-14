from rest_framework import serializers
from .models import Interest


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "project", "message", "contact_opt_in", "status"]
        read_only_fields = ["id", "status"]
