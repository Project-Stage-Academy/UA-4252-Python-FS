from elasticsearch_dsl.response import Response as ESResponse


def extract_facets(es_response: ESResponse) -> dict:
    """
    Extracts Elasticsearch aggregation results "facets"
    from the executed Search response.

    :param es_response: The result of calling search.execute().
    :type es_response: elasticsearch_dsl.response.Response

    :return Mapping { facet_name: { value: count, ... } }
    :rtype: dict
    """

    facets = {}

    if not hasattr(es_response, "aggregations"):
        return facets

    for field, agg_data in es_response.aggregations.to_dict().items():
        if not field.startswith("_filter_"):
            continue

        name = field.replace("_filter_", "")
        buckets = agg_data[name]["buckets"]
        facets[name] = {b["key"]: b["doc_count"] for b in buckets}

    return facets
