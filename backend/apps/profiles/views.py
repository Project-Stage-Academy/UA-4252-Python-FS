from django.http import Http404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile

from .permissions import IsOwnerOrReadOnly
from .serializers import UnifiedProfileSerializer, UnifiedProfileUpdateSerializer

COMMON_PROFILE_FIELDS = [
    'company_name',
    'description',
    'website',
    'phone',
    'city',
    'address',
    'postal_code',
    'logo',
    'partners_brands',
    'audit_status',
]

STARTUP_FIELDS = ['founded_year', 'team_size']

INVESTOR_FIELDS = [
    'investment_range_min',
    'investment_range_max',
    'full_name',
    'preferred_industries',
    'country',
    'region',
]

REQUIRED_FOR_PUBLISH_COMMON = [
    'company_name',
    'description',
    'email',
]

REQUIRED_FOR_PUBLISH_STARTUP = [
    'founded_year',
]

REQUIRED_FOR_PUBLISH_INVESTOR = [
    'investment_range_min',
    'investment_range_max',
    'full_name',
]


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsOwnerOrReadOnly]

    def _get_profile_object(self, pk):
        try:
            profile = InvestorProfile.objects.get(id=pk)
        except InvestorProfile.DoesNotExist:
            try:
                profile = StartupProfile.objects.get(id=pk)
            except StartupProfile.DoesNotExist:
                raise Http404("Profile not found")

        self.check_object_permissions(self.request, profile)

        return profile

    def retrieve(self, request, pk=None):
        profile = self._get_profile_object(pk)

        serializer = UnifiedProfileSerializer(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def _update_profile_fields(self, profile, validated_data):
        if isinstance(profile, StartupProfile):
            profile_type = 'startup'
        elif isinstance(profile, InvestorProfile):
            profile_type = 'investor'

        for field in COMMON_PROFILE_FIELDS:
            if field in validated_data:
                setattr(profile, field, validated_data[field])

        if profile_type == 'startup':
            for field in STARTUP_FIELDS:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])

        elif profile_type == 'investor':
            for field in INVESTOR_FIELDS:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])

        profile.save()
        return profile

    def partial_update(self, request, pk=None):
        profile = self._get_profile_object(pk)

        update_serializer = UnifiedProfileUpdateSerializer(
            data=request.data, partial=True
        )

        if not update_serializer.is_valid():
            return Response(
                update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        updated_profile = self._update_profile_fields(
            profile, update_serializer.validated_data
        )

        response_serializer = UnifiedProfileSerializer(updated_profile)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        profile = self._get_profile_object(pk)

        update_serializer = UnifiedProfileUpdateSerializer(
            data=request.data, partial=False
        )

        if not update_serializer.is_valid():
            return Response(
                update_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        updated_profile = self._update_profile_fields(
            profile, update_serializer.validated_data
        )

        response_serializer = UnifiedProfileSerializer(updated_profile)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def validate_for_publishing(self, profile):
        missing = []

        for field in REQUIRED_FOR_PUBLISH_COMMON:
            if not getattr(profile, field, None):
                missing.append(field)

        if isinstance(profile, StartupProfile):
            for field in REQUIRED_FOR_PUBLISH_STARTUP:
                if not getattr(profile, field, None):
                    missing.append(field)

        elif isinstance(profile, InvestorProfile):
            for field in REQUIRED_FOR_PUBLISH_INVESTOR:
                if not getattr(profile, field, None):
                    missing.append(field)

        return missing

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def publish(self, request, pk=None):
        profile = self._get_profile_object(pk)

        if profile.is_published:
            return Response(
                {'detail': 'Profile is already published.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        missing_fields = self.validate_for_publishing(profile)

        if missing_fields:
            return Response(
                {'error': 'Profile incomplete', 'missing_fields': missing_fields},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.is_published = True
        profile.published_at = timezone.now()
        profile.published_by_id = request.user.id
        profile.save()

        serializer = UnifiedProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
