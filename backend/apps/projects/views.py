from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Project
from .serializers import ProjectReadSerializer, ProjectWriteSerializer
from .pagination import ProjectPagination


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ProjectPagination 
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProjectReadSerializer
        return ProjectWriteSerializer

    def get_queryset(self):
        startup_id = self.kwargs.get('startup_id')
        queryset = Project.objects.filter(startup_id=startup_id).order_by('id')
        return queryset


    def perform_create(self, serializer):
        startup_id = self.kwargs.get('startup_pk')
        if not startup_id:
            raise NotFound("Startup ID missing from URL.")
        serializer.save(startup_id=startup_id)
