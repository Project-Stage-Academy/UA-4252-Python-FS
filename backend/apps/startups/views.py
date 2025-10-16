from rest_framework import viewsets, mixins
from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer
from django.db.models import Count

class StartupPublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = StartupProfile.objects.annotate(followers_count=Count('savedstartup'))
    serializer_class = StartupPublicProfileSerializer