from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Subquery, OuterRef, Value, IntegerField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import StartupFilter
from .models import StartupProfile
from .pagination import StartupPagination
from .serializers import StartupPublicProfileSerializer
from apps.investors.models import SavedItem


class StartupPublicProfileViewSet(viewsets.ModelViewSet):
    queryset = StartupProfile.objects.all()

    serializer_class = StartupPublicProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StartupPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = StartupFilter

    def get_queryset(self):
        """
        Returns a queryset of all startup profiles annotated
        with the number of followers each has.
        """
        startup_ct = ContentType.objects.get_for_model(StartupProfile)

        # subquery to count SavedItem records each startup has
        followers_subquery = (
            SavedItem.objects
            .filter(target_type=startup_ct, target_id=OuterRef("id"))
            .values("target_id")
            .annotate(count=Count("id"))
            .values("count")
        )

        # annotate each startup with the followers count
        return self.queryset.annotate(
            followers_count=Coalesce(
                Subquery(followers_subquery, output_field=IntegerField()),
                Value(0)  # default value if no SavedItem records found
            )
        ).order_by("-created_at", "-updated_at")
