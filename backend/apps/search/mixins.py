class SearchFilterValidationMixin:
    """
    Validates supported filters for Document-based search views.
    Ensures that filtering by fields not defined in 'filter_fields'
    results in an empty result set.
    """

    base_allowed_params = {
        "search",
        "ordering",
        "facet",
        "page",
        "page_size",
    }

    def _has_unsupported_filters(self, request):
        if not hasattr(self, "filter_fields"):
            raise AttributeError(
                f"{self.__class__.__name__} requires 'filter_fields' "
                f"to be defined when using SearchFilterValidationMixin."
            )

        allowed_params = set(self.base_allowed_params) | set(self.filter_fields.keys())

        for param in request.query_params.keys():
            base = param.split("__", 1)[0]  # exclude lookup expressions
            if base not in allowed_params:
                return True

        return False
