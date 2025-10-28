from django.db.models import Count
from rest_framework import mixins, viewsets

from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer


class StartupPublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "id"
    lookup_url_kwarg = "id"
    queryset = StartupProfile.objects.annotate(
        followers_count=Count("saved_by_investors")
    )

    serializer_class = StartupPublicProfileSerializer
