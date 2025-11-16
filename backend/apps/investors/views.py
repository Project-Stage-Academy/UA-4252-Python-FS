from django.db import IntegrityError, transaction 
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound

from apps.investors.models import Tracking, Investment
from apps.projects.models import Project
from apps.startups.models import StartupProfile
from apps.startups.pagination import StartupPagination

from .permissions import IsTrackingOwner, IsInvestorSelf, IsInvestor, IsOwnerOrAdmin
from .serializers import (
    TrackingCreateSerializer,
    TrackingListSerializer,
    TrackedStartupSerializer,
    TrackedProjectSerializer,
    InvestmentCreateSerializer, 
    InvestmentUpdateSerializer, 
    InvestmentListSerializer,
)

from django.shortcuts import get_object_or_404

User = get_user_model()


class TrackingViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet for creating (POST /api/tracking/) and
    deleting (DELETE /api/tracking/{id}/) Tracking records.
    """
    queryset = Tracking.objects.all()
    serializer_class = TrackingCreateSerializer

    def get_permissions(self):
        """
        POST (create) - needs only authentication.
        DELETE (destroy) - needs authentication + IsTrackingOwner.
        """
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTrackingOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override for idempotence.
        If the record already exists, it returns 200 OK instead of 400.
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
    View for the investor's list of tracked objects.
    GET /api/investors/{investor_id}/tracking/ 
    """
    serializer_class = TrackingListSerializer
    permission_classes = [IsAuthenticated, IsInvestorSelf]
    pagination_class = StartupPagination 

    def get_queryset(self):
        """
        Returns a list of 'Tracking' for the investor,
        filtered by 'target_type'.
        """
        investor_id = self.kwargs.get('investor_id')
        target_type = self.request.query_params.get('type')

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
        Override to add 'target' (startup/project) data
        to the response, avoiding N+1 queries.
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
        A helpful method for optimized loading 
        of startup or project data.
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
    

class InvestmentViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    
    queryset = Investment.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return InvestmentCreateSerializer
        elif self.action == 'partial_update':
            return InvestmentUpdateSerializer
        return InvestmentListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsInvestor()]
        elif self.action == 'partial_update':
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return [IsAuthenticated()]

class InvestorInvestmentsListView(generics.ListAPIView):
    
    serializer_class = InvestmentListSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        investor_id = self.kwargs.get('id')
        investor = get_object_or_404(User, pk=investor_id)
        
        if not self.request.user.is_staff and self.request.user.pk != investor.pk:
            raise PermissionDenied("You can only view your own investments.")

        return Investment.objects.filter(investor=investor).order_by('-created_at')
