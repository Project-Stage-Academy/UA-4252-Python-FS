from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        investor_profile = getattr(self.request.user, 'investor_profile', None)

        if investor_profile:
            return Notification.objects.filter(
                user=investor_profile
            ).select_related('related_project')
        return Notification.objects.none()

    @action(detail=True, methods=['patch'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_read = serializer.validated_data.get('is_read', True)
        notification.is_read = is_read

        if is_read and not notification.read_at:
            notification.read_at = timezone.now()
        elif not is_read:
            notification.read_at = None

        notification.save(update_fields=['is_read', 'read_at'])

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        investor_profile = getattr(request.user, 'investor_profile', None)

        if not investor_profile:
            return Response(
                {'detail': 'Investor profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        updated_count = Notification.objects.filter(
            user=investor_profile,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now())
        return Response(
            {'message': f'{updated_count} notifications marked as read.'},
            status=status.HTTP_200_OK
        )