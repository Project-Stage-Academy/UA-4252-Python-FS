from rest_framework import viewsets
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer
from .pagination import ProjectPagination

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination 

    def get_queryset(self):
        startup_id = self.kwargs['startup_id']
        return Project.objects.filter(startup__id=startup_id).order_by('id')  


