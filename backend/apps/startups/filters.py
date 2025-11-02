import django_filters

from .models import StartupProfile


class StartupFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(
        field_name="company_name",
        lookup_expr="icontains"
    )
    tag = django_filters.CharFilter(
        field_name="tags",
        lookup_expr="icontains",
    )

    class Meta:
        model = StartupProfile
        fields = ["company_name", "tag"]
