from django_fsm import can_proceed, get_available_FIELD_transitions  # noqa: F401
from rest_framework import serializers

from apps.common.constants import PROJECT_TRANSITIONS

from .models import Project, ProjectAudit


class ProjectStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Project.Status.choices)
    force = serializers.BooleanField(default=False, required=False)


class ProjectSerializer(serializers.ModelSerializer):
    can_transition_to = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'funded_at',
            'status',
            'slug',
            'is_deleted',
            'deleted_at',
            'deleted_by',
        ]

    def get_can_transition_to(self, obj):
        transitions = []
        for method_name, target_status in PROJECT_TRANSITIONS.items():
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                if can_proceed(method):
                    transitions.append(target_status)

        return transitions

    def validate(self, data):
        raised = data.get(
            'raised_amount', self.instance.raised_amount if self.instance else 0
        )
        target = data.get(
            'target_amount', self.instance.target_amount if self.instance else 0
        )
        allow_over = data.get(
            'allow_overfunding',
            self.instance.allow_overfunding if self.instance else False,
        )

        if not allow_over and raised > target:
            raise serializers.ValidationError(
                {
                    'raised_amount': f'Cannot exceed target ({target}). '
                    f'Set allow_overfunding=true first.'
                }
            )

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
        read_only_fields = ['id', 'slug', 'raised_amount', 'created_at']

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
    can_transition_to = serializers.SerializerMethodField()

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
            'allow_overfunding',
            'currency',
            'thumbnail',
            'tags',
            'progress_percentage',
            'visibility',
            'funded_at',
            'can_transition_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'slug',
            'raised_amount',
            'status',
            'funded_at',
            'created_at',
            'updated_at',
        ]

    def get_progress_percentage(self, obj):
        if obj.target_amount and obj.target_amount > 0:
            return round((float(obj.raised_amount) / float(obj.target_amount)) * 100, 2)
        return 0.0

    def get_can_transition_to(self, obj):
        transitions = []
        for method_name, target_status in PROJECT_TRANSITIONS.items():
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                if can_proceed(method):
                    transitions.append(target_status)

        return transitions


class ProjectsCreateUpdateSerialiser(serializers.ModelSerializer):
    """Serializer for creating and updating projects"""

    class Meta:
        model = Project
        fields = [
            'title',
            'short_description',
            'description',
            'thumbnail',
            'target_amount',
            'raised_amount',
            'allow_overfunding',
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

    def update(self, instance, validated_data):
        old_raised = instance.raised_amount
        instance = super().update(instance, validated_data)
        if 'raised_amount' in validated_data and instance.raised_amount != old_raised:
            instance.check_auto_funding()
        return instance

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


class ProjectAuditSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(
        source='user.email', read_only=True, allow_null=True
    )
    user_name = serializers.SerializerMethodField()
    changed_fields_display = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAudit
        fields = [
            'id',
            'action',
            'timestamp',
            'user_email',
            'user_name',
            'changes',
            'changed_fields_display',
            'user_agent',
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        if obj.user:
            return (
                f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
            )
        return "System"

    def get_changed_fields_display(self, obj):
        changes = obj.changes or {}
        changed_fields = changes.get('changed_fields', [])

        field_labels = {
            'title': 'Title',
            'short_description': 'Short Description',
            'description': 'Description',
            'status': 'Status',
            'target_amount': 'Target Amount',
            'raised_amount': 'Raised Amount',
            'allow_overfunding': 'Allow Overfunding',
            'currency': 'Currency',
            'funded_at': 'Funded At',
            'thumbnail': 'Thumbnail',
            'tags': 'Tags',
            'visibility': 'Visibility',
            'is_deleted': 'Deleted',
            'deleted_at': 'Deleted At',
            'deleted_by': 'Deleted By',
        }

        return [
            field_labels.get(field, field.replace('_', ' ').title())
            for field in changed_fields
        ]
