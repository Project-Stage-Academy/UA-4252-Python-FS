from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django_fsm import TransitionNotAllowed, can_proceed # noqa: F401

from apps.startups.models import StartupProfile

from .models import Project
from .pagination import ProjectPagination
from .permissions import IsOwnerOrReadOnly, IsStartupOwner
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectsCreateUpdateSerialiser,
    ProjectSerializer,
    ProjectStatusSerializer
)
from django.utils import timezone

from apps.common.constants import PROJECT_TRANSITIONS


class ProjectViewSet(viewsets.ModelViewSet):
    pagination_class = ProjectPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectsCreateUpdateSerialiser
        elif self.action == 'update_status':
            return ProjectStatusSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.select_related(
            'startup', 'startup__user').filter(is_deleted=False)

        if 'startup_pk' in self.kwargs:
            startup_pk = self.kwargs['startup_pk']
            queryset = queryset.filter(startup_id=startup_pk)

            if self.request.user.is_authenticated:
                try:
                    startup = StartupProfile.objects.get(pk=startup_pk)
                    if startup.user != self.request.user:
                        queryset = queryset.filter(
                            visibility__in=['public', 'unlisted']
                        )
                except StartupProfile.DoesNotExist:
                    queryset = queryset.none()
            else:
                queryset = queryset.filter(visibility__in=['public', 'unlisted'])

        return queryset.order_by('-created_at')

    def get_object(self):
        queryset = Project.objects.select_related(
            'startup', 'startup__user').filter(is_deleted=False)

        if 'startup_pk' in self.kwargs:
            queryset = queryset.filter(startup_id=self.kwargs['startup_pk'])

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def get_permissions(self):
        if self.action == 'create':
            return [IsStartupOwner()]
        return [IsOwnerOrReadOnly()]

    def list(self, request, *args, **kwargs):
        startup_pk = self.kwargs.get('startup_pk')
        if not startup_pk:
            raise NotFound('Startup ID missing from URL')

        get_object_or_404(StartupProfile, pk=startup_pk)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        startup_pk = self.kwargs.get('startup_pk')
        if not startup_pk:
            raise NotFound('Startup ID missing from URL')

        startup = get_object_or_404(StartupProfile, pk=startup_pk)

        serializer = self.get_serializer(
            data=request.data, context={'startup': startup, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_success_headers(self, data):
        try:
            return {'Location': f"/api/projects/{data['id']}/"}
        except (TypeError, KeyError):
            return {}

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete(user=request.user)

        return Response(
            {'detail': 'Project successfully deleted'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None, **kwargs):
        project = self.get_object()
        serializer = ProjectStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        force = serializer.validated_data.get('force', False)

        if project.startup.user != request.user:
            return Response({
                'error': 'Only user who create project can change status'
            }, status=status.HTTP_403_FORBIDDEN)

        if new_status == project.status:
            return Response({'message': 'Already in this status'})

        if force and new_status in Project.Status.values:
            project.status = new_status
            if new_status == Project.Status.FUNDED:
                project.funded_at = timezone.now()
            project.save()
            return Response(ProjectSerializer(project).data)

        transition_method = PROJECT_TRANSITIONS.get(new_status)
        if not transition_method:
            return Response(
                {'error': f'Unknown status: {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            method = getattr(project, transition_method)
            method()
            project.save()
            return Response(ProjectSerializer(project).data)

        except TransitionNotAllowed:
            return Response({
                'error': f'Cannot transition from {project.status} to {new_status}',
                'current_status': project.status,
                'allowed_transitions': self._get_allowed_transitions(project)
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_allowed_transitions(self, project):
        allowed = []
        for method_name, target_status in PROJECT_TRANSITIONS.items():
            if hasattr(project, method_name):
                method = getattr(project, method_name)
                if can_proceed(method):
                    allowed.append(target_status)

        return allowed

    def perform_update(self, serializer):
        old_visibility = serializer.instance.visibility
        instance = serializer.save()
        if old_visibility != instance.visibility and instance.visibility == 'public':
            # Task 6 - Index project in search
            pass
