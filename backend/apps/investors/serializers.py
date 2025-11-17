from django.db import IntegrityError
from rest_framework import serializers
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator

from apps.investors.models import Tracking, Investment
from apps.projects.models import Project
from apps.startups.models import StartupProfile

from apps.projects.serializers import ProjectListSerializer
from apps.startups.serializers import StartupPublicProfileSerializer

class TrackingCreateSerializer(serializers.ModelSerializer):
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
        return super().create(validated_data)


class TrackedStartupSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Project
        fields = ['id', 'title', 'slug', 'thumbnail']


class TrackingListSerializer(serializers.ModelSerializer):
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

class InvestmentCreateSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), 
        write_only=True, 
        pk_field=serializers.UUIDField()
    )
    
    amount_committed = serializers.DecimalField(
        max_digits=18, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = serializers.RegexField(
        r'^[A-Z]{3}$', 
        error_messages={'invalid': 'Currency code must be in ISO-4217 format (e.g., "USD").'}
    )
    meta = serializers.JSONField(required=False)

    class Meta:
        model = Investment
        fields = [
            'id', 
            'project', 
            'amount_committed', 
            'currency', 
            'meta', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate_project(self, project_instance):
        if project_instance.visibility not in ['public', 'investor_allowed']: 
            raise serializers.ValidationError("You cannot invest in this project (not public).")

        FUNDRAISING_STATUS = getattr(settings, 'FUNDRAISING_STATUS', 'fundraising')
        if project_instance.status != FUNDRAISING_STATUS:
            raise serializers.ValidationError(f"The project is not currently fundraising (status: {project_instance.status}).")
        
        return project_instance

    def create(self, validated_data):
        project = validated_data.pop('project')
        user = self.context['request'].user
        
        validated_data['status'] = 'committed'
        
        return Investment.objects.create(
            investor=user, 
            project=project, 
            **validated_data
        )

class InvestmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['amount_invested', 'status', 'meta']
        extra_kwargs = {
            'amount_invested': {'required': False},
            'status': {'required': False},
            'meta': {'required': False},
        }

class InvestmentListSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = Investment
        fields = [
            'id', 
            'project_title', 
            'amount_committed', 
            'amount_invested', 
            'currency', 
            'status', 
            'created_at'
        ]