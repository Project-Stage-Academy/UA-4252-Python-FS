from rest_framework import serializers
from .models import Project


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects"""
    startup_name = serializers.CharField(source='startup.name', read_only=True)
    startup_slug = serializers.CharField(source='startup.slug', read_only=True)
    progress_percentage = serializers.ReadOnlyField()

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


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed project"""
    startup_id = serializers.UUIDField(source='startup.id', read_only=True)
    startup_name = serializers.CharField(source='startup.name', read_only=True)
    startup_slug = serializers.CharField(source='startup.slug', read_only=True)
    owner_email = serializers.CharField(source='startup.owner.email', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    class Meta:
        model = Project
        fields = [
            'id',
            'startup_id',
            'startup_name',
            'startup_slug',
            'owner_email'
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
            'progress_percentage'
            'visibility',
            'created_at',
            'update_at'
        ]
        read_only_fields = [
            'id',
            'raised_amount',
            'created_at',
            'update_at'
        ]

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
                raise serializers.ValidationError({
                    'target_amount': f'Target amount cannot be less than already raised amount ({self.instance.raised_amount})'
                })
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