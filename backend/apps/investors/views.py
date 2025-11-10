from django.db import IntegrityError, transaction 
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound

from apps.investors.models import Tracking
from apps.projects.models import Project
from apps.startups.models import StartupProfile
from apps.startups.pagination import StartupPagination

from .permissions import IsTrackingOwner
from .serializers import (
    TrackingCreateSerializer,
    TrackingListSerializer,
    TrackedStartupSerializer,
    TrackedProjectSerializer,
)

User = get_user_model()


class TrackingViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet для Створення (POST /api/tracking/) та
    Видалення (DELETE /api/tracking/{id}/) записів Tracking.
    """
    queryset = Tracking.objects.all()
    serializer_class = TrackingCreateSerializer

    def get_permissions(self):
        """
        POST (create) - потрібна лише аутентифікація.
        DELETE (destroy) - потрібна аутентифікація + IsTrackingOwner.
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTrackingOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Перевизначено для ідемпотентності.
        Якщо запис вже існує, повертає 200 OK замість 400.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except IntegrityError:
            instance = Tracking.objects.get(
                investor=request.user,
                target_type=serializer.validated_data['target_type'],
                target_id=serializer.validated_data['target_id']
            )
            return Response(
                self.get_serializer(instance).data, status=status.HTTP_200_OK
            )


class InvestorTrackingListView(generics.ListAPIView):
    """
    View для списку відстежуваних об'єктів інвестора.
    GET /api/investors/{investor_id}/tracking/
    """
    serializer_class = TrackingListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StartupPagination 

    def get_queryset(self):
        """
        Повертає список 'Tracking' для інвестора,
        відфільтрований за 'target_type'.
        """
        investor_id = self.kwargs.get('investor_id')
        target_type = self.request.query_params.get('type')

        if self.request.user.id != investor_id:
            raise PermissionDenied("Ви можете переглядати лише власні відстеження.")

        try:
            User.objects.get(pk=investor_id)
        except User.DoesNotExist:
            raise NotFound("Інвестора не знайдено.")

        queryset = Tracking.objects.filter(investor_id=investor_id)

        if target_type in ['startup', 'project']:
            queryset = queryset.filter(target_type=target_type)
        else:
             return queryset.none() 

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """
        Перевизначено для додавання даних про 'target' (startup/project)
        до відповіді, уникаючи N+1 запитів.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            results = self.fetch_and_inject_targets(request, serializer.data)
            return self.get_paginated_response(results)

        serializer = self.get_serializer(queryset, many=True)
        results = self.fetch_and_inject_targets(request, serializer.data)
        return Response(results)

    def fetch_and_inject_targets(self, request, tracking_data):
        """
        Допоміжний метод для оптимізованого завантаження
        даних про стартапи або проекти.
        """
        if not tracking_data:
            return tracking_data

        if not tracking_data:
            return tracking_data

        target_type = tracking_data[0]['target_type']
        target_ids = [item['target_id'] for item in tracking_data]
        
        targets_map = {}
        serializer_context = {'request': request}

        if target_type == 'startup':
            targets = StartupProfile.objects.filter(pk__in=target_ids)
            targets_map = {
                str(t.pk): TrackedStartupSerializer(t, context=serializer_context).data
                for t in targets
            }
        
        elif target_type == 'project':
            targets = Project.objects.filter(pk__in=target_ids)
            targets_map = {
                str(t.pk): TrackedProjectSerializer(t, context=serializer_context).data
                for t in targets
            }


        for item in tracking_data:
            item['target'] = targets_map.get(str(item['target_id']))

        return tracking_data