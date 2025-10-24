from rest_framework import viewsets, mixins
from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer
from django.db.models import Count

class StartupPublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    queryset = StartupProfile.objects.annotate(followers_count=Count('saved_by_investors'))
    
    serializer_class = StartupPublicProfileSerializer