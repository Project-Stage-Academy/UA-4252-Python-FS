from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class GetHealth(APIView):
    """ Simple health-check endpoint to check health. """

    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
