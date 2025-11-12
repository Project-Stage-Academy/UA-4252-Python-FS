from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, exceptions

from apps.investors.models import InvestorProfile, SavedItem
from .serializers import SavedItemCreateSerializer


class SavedItemViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = SavedItem.objects.all()
    serializer_class = SavedItemCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "saved_item_id"

    def get_investor(self):
        investor_id = self.kwargs.get("investor_id")
        investor = InvestorProfile.objects.get(id=investor_id)

        if investor.user != self.request.user:
            raise exceptions.NotFound("Investor not found.")

        return investor

    def get_queryset(self):
        investor = self.get_investor()
        return self.queryset.filter(investor=investor)

    def perform_create(self, serializer):
        investor = self.get_investor()
        serializer.save(investor=investor)
