from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from .models import Interest
from .serializers import InterestSerializer


class ExpressInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get("project_id")

        # Проверяем проект
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=404)

        serializer = InterestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = Interest.objects.create(
            investor=request.user,
            project=project,
            message=serializer.validated_data.get("message"),
            contact_opt_in=serializer.validated_data.get("contact_opt_in", False),
        )

        return Response(
            {
                "id": str(interest.id),
                "project_id": str(project.id),
                "investor": request.user.id,
                "status": interest.status,
            },
            status=201,
        )
