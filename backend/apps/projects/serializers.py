from rest_framework import serializers
from django_fsm import can_proceed
from .models import Project

class ProjectStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Project.Status.choices)
    force = serializers.BooleanField(default=False, required=False)

class ProjectSerializer(serializers.ModelSerializer):
    can_transition_to = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['funded_at', 'status']

    def get_can_transition_to(self, obj):
        transitions = []
        for method_name in ['start_mvp', 'start_fundraising', 'mark_funded', 'close_project']:
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                if can_proceed(method):
                    transitions.append(method._django_fsm.target)
        return transitions

    def validate(self, data):
        raised = data.get('raised_amount', self.instance.raised_amount if self.instance else 0)
        target = data.get('target_amount', self.instance.target_amount if self.instance else 0)

        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        if 'raised_amount' in validated_data:
            instance.check_auto_funding()

        return instance

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects"""

    startup_name = serializers.CharField(source='startup.company_name', read_only=True)
    startup_slug = serializers.CharField(source='startup.slug', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'slug',
            'short_description',
            'status',
            'thumbnail',
            'target_amount',
            'raised_amount',
            'currency',
            'progress_percentage',
            'visibility',
            'startup_name',
            'startup_slug',
            'created_at',
        ]
        read_only_fields = ['id', 'raised_amount', 'created_at']

    def get_progress_percentage(self, obj):
        if obj.target_amount and obj.target_amount > 0:
            return round((float(obj.raised_amount) / float(obj.target_amount)) * 100, 2)
        return 0.0


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed project"""

    startup_id = serializers.UUIDField(source='startup.id', read_only=True)
    startup_name = serializers.CharField(source='startup.company_name', read_only=True)
    startup_slug = serializers.CharField(source='startup.slug', read_only=True)
    email = serializers.CharField(source='startup.user.email', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'startup_id',
            'startup_name',
            'startup_slug',
            'email',
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
            'progress_percentage',
            'visibility',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'raised_amount',
            'created_at',
            'updated_at',
        ]

    def get_progress_percentage(self, obj):
        if obj.target_amount and obj.target_amount > 0:
            return round((float(obj.raised_amount) / float(obj.target_amount)) * 100, 2)
        return 0.0


class ProjectsCreateUpdateSerialiser(serializers.ModelSerializer):
    """Serializer for creating and updating projects"""

    class Meta:
        model = Project
        fields = [
            'title',
            'short_description',
            'description',
            'thumbnail',
            'status',
            'target_amount',
            'currency',
            'tags',
            'visibility',
        ]

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than 0")
        return value

    def validate(self, data):
        """Validate business rules"""
        if self.instance:
            target_amount = data.get('target_amount', self.instance.target_amount)
            if self.instance.raised_amount > target_amount:
                error_message = (
                    f'Target amount cannot be less than already raised amount '
                    f'({self.instance.raised_amount})'
                )
                raise serializers.ValidationError({'target_amount': error_message})
        return data

    def create(self, validated_data):
        """Create the project with startup from contex"""
        startup = self.context.get('startup')
        if not startup:
            raise serializers.ValidationError('Startup is required')
        validated_data['startup'] = startup
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return detailed representation after create/update"""
        return ProjectDetailSerializer(instance, context=self.context).data
