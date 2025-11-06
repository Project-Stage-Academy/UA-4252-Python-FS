from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import StartupFilter
from .models import StartupProfile
from .pagination import StartupPagination
from .serializers import StartupPublicProfileSerializer


class StartupPublicProfileViewSet(viewsets.ModelViewSet):
    queryset = (
        StartupProfile.objects
        .annotate(followers_count=Count("saved_by_investors"))
        .order_by("-created_at", "-updated_at")
    )  # annotate() can result in an unordered queryset

    serializer_class = StartupPublicProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StartupPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = StartupFilter
