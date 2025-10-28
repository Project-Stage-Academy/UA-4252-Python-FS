from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Project
from .serializers import ProjectListSerializer, ProjectsCreateUpdateSerialiser, ProjectDetailSerializer
from .pagination import ProjectPagination
from apps.startups.models import StartupProfile

from .permissions import IsOwnerOrReadOnly, IsStartupOwner
from .pagination import ProjectPagination


class ProjectViewSet(viewsets.ModelViewSet):
    pagination_class = ProjectPagination
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectsCreateUpdateSerialiser
        return ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.select_related('startup', 'startup__user')
        queryset = Project.objects.filter(is_deleted=False)

        if 'startup_pk' in self.kwargs:
            startup_pk = self.kwargs['startup_pk']
            queryset = queryset.filter(startup_id=startup_pk)

            if self.request.user.is_authenticated:
                try:
                    startup = StartupProfile.objects.get(pk=startup_pk)
                    if startup.user != self.request.user:
                        queryset = queryset.filter(visibility__in=['public', 'unlisted'])
                except StartupProfile.DoesNotExit:
                    queryset = queryset.none()
            else:
                queryset = queryset.filter(visibility__in=['public', 'unlisted'])

        return queryset.order_by('-created_at')

    # Move to def create
    # def perform_create(self, serializer):
    #     startup_id = self.kwargs.get('startup_pk')
    #     if not startup_id:
    #         raise NotFound("Startup ID missing from URL.")
    #     serializer.save(startup_id=startup_id)

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
            data=request.data,
            context={'startup': startup, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_success_headers(self, data):
        try:
            return {
                'Location': f"/api/projects/{data['id']}/"
            }
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
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
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
            status=status.HTTP_204_NO_CONTENT
        )

