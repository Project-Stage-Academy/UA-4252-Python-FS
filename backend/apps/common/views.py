from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connections
from django.db.utils import OperationalError


class GetHealth(APIView):
    """Simple health-check endpoint to check health."""

    def get(self, request):
        db_conn = connections['default']
        try:
            db_conn.ensure_connection()
            db_conn.cursor().execute('SELECT 1;')
        except OperationalError:
            return Response(
                {
                    'status': 'unhealthy',
                    'db': 'unreachable',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                'status': 'ok',
                'db': 'connected',
            },
            status=status.HTTP_200_OK
        )
