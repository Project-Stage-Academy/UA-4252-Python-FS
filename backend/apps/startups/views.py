from rest_framework import viewsets, mixins
from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer
from django.db.models import Count
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class StartupPublicProfileViewSet(viewsets.ModelViewSet):
    # lookup_field = 'id'
    # lookup_url_kwarg = 'id'
    queryset = StartupProfile.objects.all
    
    serializer_class = StartupPublicProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return StartupProfile.objects.all().order_by('-created_at')
