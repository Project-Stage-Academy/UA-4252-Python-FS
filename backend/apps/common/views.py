from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Any

from rest_framework import permissions
from rest_framework.request import Request


class GetHealth(APIView):
    """Simple health-check endpoint to check health."""

    def get(self, request):
        db_conn = connections["default"]
        try:
            db_conn.ensure_connection()
            db_conn.cursor().execute("SELECT 1;")
        except OperationalError:
            return Response(
                {
                    "status": "unhealthy",
                    "db": "unreachable",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "status": "ok",
                "db": "connected",
            },
            status=status.HTTP_200_OK,
        )


def health(request):
    return JsonResponse({"status": "ok"})

class LandingContentAPIView(APIView):
    """
    Returns static content for the main landing page.

    Provides all text, cards, and links needed by the frontend
    to render the page in a single JSON object.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        content_data = {
            "hero": {
                "title": "Where Great Ideas Get Funded",
                "subtitle": "Connecting the most innovative startups with visionary investors.",
                "cta_text": "Get Started",
                "hero_images": [
                    {"url": "/static/images/hero_main.png"},
                    {"url": "/static/images/hero_secondary.png"},
                ],
            },
            "for_whom": [
                {
                    "icon": "startup",
                    "title": "For Startups",
                    "desc": "Pitch your vision, secure funding, and access the resources to scale your business.",
                },
                {
                    "icon": "investor",
                    "title": "For Investors",
                    "desc": "Discover curated, high-potential startups and invest in the next generation of innovation.",
                },
                {
                    "icon": "expert",
                    "title": "For Experts",
                    "desc": "Join our network to mentor founders and advise on industry-specific challenges.",
                },
            ],
            "why_worth": [
                {
                    "title": "Curated Deal Flow",
                    "desc": "Access a vetted pipeline of startups that align with your investment thesis.",
                },
                {
                    "title": "Streamlined Process",
                    "desc": "From discovery to due diligence, our platform simplifies the entire investment cycle.",
                },
                {
                    "title": "Community & Network",
                    "desc": "Connect with founders, co-investors, and industry leaders.",
                },
            ],
            "footer_links": {
                "left": [
                    {"text": "About Us", "url": "/about"},
                    {"text": "Contact", "url": "/contact"},
                    {"text": "FAQ", "url": "/faq"},
                ],
                "right": [
                    {"text": "Privacy Policy", "url": "/privacy"},
                    {"text": "Terms of Use", "url": "/terms"},
                ],
            },
        }
        return Response(content_data)