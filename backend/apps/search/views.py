from collections import defaultdict

from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
    FacetedFilterSearchFilterBackend,
    HighlightBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .documents import (
    StartupDocument,
    ProjectDocument,
)
from .mixins import SearchFilterValidationMixin
from .pagination import StartupsProjectsSearchPagination
from .serializers import (
    StartupDocumentSerializer,
    ProjectDocumentSerializer,
)
from .utils import extract_facets


class StartupElasticSearchView(
    DocumentViewSet,
    SearchFilterValidationMixin,
):
    """
    Handles full-text search for the "startups" Elasticsearch index.
    Pagination is intentionally disabled.
    Response format:
    {
        "results": [...],   # serialized startup documents
        "facets": {...}     # aggregations, extracted from ES response
    }
    """
    document = StartupDocument
    serializer_class = StartupDocumentSerializer
    pagination_class = None
    lookup_field = "id"

    filter_backends = [
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
        FacetedFilterSearchFilterBackend,
        HighlightBackend,
    ]

    search_fields = [
        "company_name",
        "description",
    ]

    filter_fields = {
        "tag": "tags",
        "city": "city",
    }

    highlight_fields = {
        "company_name": {"enabled": True},
        "description": {"enabled": True},
    }

    faceted_search_fields = {
        "tags": {"enabled": True},
        "city": {"enabled": True},
    }

    def list(self, request, *args, **kwargs):
        if self._has_unsupported_filters(request):
            return Response({
                "results": [],
                "facets": {},
            })

        search = self.filter_queryset(self.get_queryset())
        es_response = search[0:100].execute()  # fetch up to 100 documents

        results = self.get_serializer(es_response.hits, many=True).data
        facets = extract_facets(es_response)

        return Response({
            "results": results,
            "facets": facets,
        })


class ProjectElasticSearchView(
    DocumentViewSet,
    SearchFilterValidationMixin,
):
    """
    Handles full-text search for the "projects" Elasticsearch index.
    Pagination is intentionally disabled.
    Response format:
    {
        "results": [...],   # serialized project documents
        "facets": {...}     # aggregations, extracted from ES response
    }
    """
    document = ProjectDocument
    serializer_class = ProjectDocumentSerializer
    pagination_class = None
    lookup_field = "id"

    filter_backends = [
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
        FacetedFilterSearchFilterBackend,
        HighlightBackend,
    ]

    search_fields = [
        "title",
        "short_description",
        "description",
    ]

    filter_fields = {
        "tag": "tags",
        "status": "status",
    }

    highlight_fields = {
        "title": {"enabled": True},
        "short_description": {"enabled": True},
        "description": {"enabled": True},
    }

    faceted_search_fields = {
        "tags": {"enabled": True},
        "status": {"enabled": True},
    }

    def list(self, request, *args, **kwargs):
        if self._has_unsupported_filters(request):
            return Response({
                "results": [],
                "facets": {},
            })

        search = self.filter_queryset(self.get_queryset())
        es_response = search[:100].execute()  # fetch up to 100 documents

        results = self.get_serializer(es_response.hits, many=True).data
        facets = extract_facets(es_response)

        return Response({
            "results": results,
            "facets": facets,
        })


class StartupsProjectsElasticSearchView(ViewSet):
    """
    Executes a single global search across two Elasticsearch
    indices: "startups" and "projects":
        - calls search views for startups and projects with the same request;
        - merges their results;
        - applies manual ordering;
        - paginates the combined dataset;
        - merges facet aggregations.
    Response format:
    {
        "count": ...,
        "next": ...,
        "previous": ...,
        "results": [...],    # combined and ordered results
        "facets": {...}      # merged facets from both indices
    }
    """
    pagination_class = StartupsProjectsSearchPagination
    ordering_fields = [
        "created_at",
        "updated_at",
        "-created_at",
        "-updated_at",
    ]
    default_ordering_field = "-created_at"

    def _order_queryset(self, request, queryset):
        ordering = request.query_params.get("ordering", self.default_ordering_field)
        if ordering not in self.ordering_fields:
            ordering = self.default_ordering_field

        reverse = ordering.startswith("-")
        field = ordering.lstrip("-")
        return sorted(queryset, key=lambda x: x[field], reverse=reverse)

    def _paginate_queryset(self, request, queryset):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(page).data

    @staticmethod
    def _merge_facets(a: dict, b: dict) -> dict:
        merged = defaultdict(dict)

        for key in set(a.keys()) | set(b.keys()):
            a_vals = a.get(key, {})
            b_vals = b.get(key, {})

            for option in set(a_vals.keys()) | set(b_vals.keys()):
                merged[key][option] = a_vals.get(option, 0) + b_vals.get(option, 0)

        return merged

    def list(self, request, *args, **kwargs):
        # get search results for startups and projects individually
        startups = (StartupElasticSearchView
                    .as_view({"get": "list"})(request._request)
                    .data)
        projects = (ProjectElasticSearchView
                    .as_view({"get": "list"})(request._request)
                    .data)

        # combine search results into a single query
        results = self._order_queryset(
            request=request,
            queryset=startups["results"] + projects["results"]
        )

        paginated = self._paginate_queryset(request, results)
        paginated["facets"] = self._merge_facets(
            a=startups["facets"],
            b=projects["facets"]
        )

        return Response(paginated, status=200)
