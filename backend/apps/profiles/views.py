from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.investors.models import InvestorProfile
from apps.startups.models import StartupProfile

from .permissions import IsOwnerOrReadOnly
from .serializers import UnifiedProfileSerializer, UnifiedProfileUpdateSerializer


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsOwnerOrReadOnly]

    def _get_profile_object(self, profile_uuid):
        try:
            return InvestorProfile.objects.get(id=profile_uuid)
        except InvestorProfile.DoesNotExist:
            pass

        try:
            return StartupProfile.objects.get(id=profile_uuid)
        except StartupProfile.DoesNotExist:
            pass

        return None

    def retrieve(self, request, pk=None):
        profile = self._get_profile_object(pk)

        if not profile:
            return Response(
                {'detail': 'No such profile exists'}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UnifiedProfileSerializer(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def _update_profile_fields(self, profile, validated_data):
        if isinstance(profile, StartupProfile):
            profile_type = 'startup'
        elif isinstance(profile, InvestorProfile):
            profile_type = 'investor'

        common_fields = [
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

        for field in common_fields:
            if field in validated_data:
                setattr(profile, field, validated_data[field])

        if profile_type == 'startup':
            startup_fields = ['founded_year', 'team_size']
            for field in startup_fields:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])

        elif profile_type == 'investor':
            investor_fields = [
                'investment_range_min',
                'investment_range_max',
                'full_name',
                'preferred_industries',
                'country',
                'region',
            ]
            for field in investor_fields:
                if field in validated_data:
                    setattr(profile, field, validated_data[field])

        profile.save()
        return profile

    def partial_update(self, request, pk=None):
        profile = self._get_profile_object(pk)

        if not profile:
            return Response(
                {'detail': 'No such profile exists'}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, profile)

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

        if profile is None:
            return Response(
                {'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, profile)

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
