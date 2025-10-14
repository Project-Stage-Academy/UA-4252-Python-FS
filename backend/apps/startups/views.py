from django.shortcuts import render
from rest_framework import viewsets, mixins
from .models import StartupProfile
from .serializers import StartupPublicProfileSerializer

class StartupPublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = StartupProfile.objects.all()
    serializer_class = StartupPublicProfileSerializer
    lookup_field = 'id'