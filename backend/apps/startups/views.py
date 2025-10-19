
from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

class StartupPublicProfileViewSet(ReadOnlyModelViewSet):
    queryset = StartupProfile.objects.all()
    serializer_class = StartupPublicProfileSerializer

    lookup_field = "id"
    lookup_url_kwarg = "id"