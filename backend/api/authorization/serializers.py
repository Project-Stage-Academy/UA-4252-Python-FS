from apps.users.models import User
from rest_framework import serializers


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        """ Need to change fields and model when User model will be available. """
        model = User
        fields = ('email', 'password')