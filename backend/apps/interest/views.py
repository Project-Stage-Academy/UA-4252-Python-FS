from rest_framework import generics, permissions
from .serializers import InterestSerializer

class ExpressInterestView(generics.CreateAPIView):
    serializer_class = InterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
