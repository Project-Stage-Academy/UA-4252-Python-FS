import django_filters

from .models import StartupProfile


class StartupFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(
        field_name="company_name",
        lookup_expr="icontains"
    )
    tag = django_filters.CharFilter(method="filter_tag")

    class Meta:
        model = StartupProfile
        fields = ["company_name", "tag"]

    def filter_tag(self, queryset, name, value):
        return queryset.filter(tags__overlap=[value])
