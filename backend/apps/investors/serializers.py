from django.db import IntegrityError
from rest_framework import serializers

from apps.investors.models import Tracking
from apps.projects.models import Project
from apps.startups.models import StartupProfile

from apps.projects.serializers import ProjectListSerializer
from apps.startups.serializers import StartupPublicProfileSerializer


class TrackingCreateSerializer(serializers.ModelSerializer):
    """
    Серіалайзер для створення (POST) об'єкта Tracking.
    Він валідує target_id і автоматично встановлює інвестора.
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
        Перевіряємо, чи існує об'єкт, який ми намагаємося відстежити.
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
        Перевизначаємо create для ідемпотентності.
        Якщо запис вже існує (завдяки unique_together), ми його повертаємо.
        """
        return super().create(validated_data)


class TrackedStartupSerializer(serializers.ModelSerializer):
    """
    Мінімальний серіалайзер для StartupProfile, як вимагає таска.
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
    Мінімальний серіалайзер для Project, як вимагає таска.
    """
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'thumbnail']


class TrackingListSerializer(serializers.ModelSerializer):
    """
    Серіалайзер для списку (GET) об'єктів Tracking.
    Поле 'target' буде додано у View для оптимізації.
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