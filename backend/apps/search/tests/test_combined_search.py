from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.projects.models import Project
from apps.search.documents import StartupDocument, ProjectDocument
from apps.startups.models import StartupProfile

User = get_user_model()


@pytest.fixture
def search_url():
    return reverse("search")


@pytest.fixture(autouse=True)
def clean_elasticsearch_indexes():
    """
    Ensures that Elasticsearch indexes used for tests are clean
    before and after each test. Creates isolated test indexes
    (test_startups, test_projects) and deletes them after use.
    """

    # create test indices
    for document in [StartupDocument, ProjectDocument]:
        document._index._name = "test_" + document._index._name
        document.init()

    yield  # run test

    # Delete test indices
    for document in [StartupDocument, ProjectDocument]:
        document._index.delete(ignore=404)
        document._index._name = document._index._name.lstrip("test_")


@pytest.fixture
def sample_data():
    now = datetime.now()

    user = User.objects.create_user(
        email="testuser@example.com",
        password="SecurePass123",
        first_name="Test",
        last_name="User",
    )

    startups = [
        StartupProfile.objects.create(
            user=user,
            company_name="Handmade Co",
            description="We make craft pottery and wood items.",
            city="Lviv",
            tags=["craft", "pottery"],
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=5),
        ),
        StartupProfile.objects.create(
            user=user,
            company_name="Tech Innovators",
            description="AI-powered SaaS tools.",
            city="Kyiv",
            tags=["tech", "ai"],
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=2),
        ),
        StartupProfile.objects.create(
            user=user,
            company_name="Woodcraft Studio",
            description="Handcrafted furniture and decor.",
            city="Lviv",
            tags=["craft", "wood"],
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1),
        ),
    ]

    projects = [
        Project.objects.create(
            startup=startups[0],
            title="Eco Pottery",
            short_description="Sustainable craft pottery project.",
            description="Handmade ceramics and eco-friendly materials.",
            status="fundraising",
            tags=["craft", "pottery"],
            target_amount=10000,
            raised_amount=5000,
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=3),
        ),
        Project.objects.create(
            startup=startups[1],
            title="Smart Home Hub",
            short_description="IoT project for smart homes.",
            description="AI integration and smart sensors.",
            status="active",
            tags=["tech", "ai"],
            target_amount=20000,
            raised_amount=15000,
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=4),
        ),
        Project.objects.create(
            startup=startups[2],
            title="Wooden Lamps",
            short_description="Wood design project.",
            description="Unique handcrafted wooden lamps.",
            status="funded",
            tags=["craft", "wood"],
            target_amount=8000,
            raised_amount=8000,
            created_at=now - timedelta(days=2),
            updated_at=now,
        ),
    ]

    return {"startups": startups, "projects": projects}


@pytest.mark.django_db
def test_empty_search_returns_all(client, search_url, sample_data):
    """
    Test empty search query returns all results.
    """
    response = client.get(search_url)
    assert response.status_code == 200

    assert len(response.data["results"]) == 6


@pytest.mark.django_db
def test_text_search(client, search_url, sample_data):
    """
    Test text search returns both startups and projects
    that match the search term.
    """
    response = client.get(search_url, {"search": "pottery"})
    assert response.status_code == 200

    results = response.data["results"]
    assert len(results) == 2

    result_types = {r["type"] for r in results}
    assert "startup" in result_types
    assert "project" in result_types

    for r in results:
        highlight = r.get("highlight", {})
        assert any("pottery" in str(v).lower() for v in highlight.values())


@pytest.mark.django_db
def test_highlight_field_in_search_results(client, search_url, sample_data):
    """
    Test highlight snippets are included when performing text search.
    """
    response = client.get(search_url, {"search": "wood"})
    assert response.status_code == 200

    results = response.data["results"]
    assert all("highlight" in item for item in results)


@pytest.mark.django_db
def test_facets_in_response(client, search_url, sample_data):
    """
    Test response contains facet aggregations for tags, city, and status.
    """
    response = client.get(search_url)
    assert response.status_code == 200

    assert "facets" in response.data
    facets = response.data["facets"]

    assert "tags" in facets
    assert "city" in facets or "status" in facets

    assert "craft" in facets["tags"]
    assert facets["tags"]["craft"] == 4


@pytest.mark.django_db
def test_filter_by_tag(client, search_url, sample_data):
    """
    Test filtering by 'tag' returns only results containing provided tag.
    """
    response = client.get(search_url, {"tag": "craft"})
    assert response.status_code == 200

    results = response.data["results"]
    for item in results:
        assert "craft" in item["tags"]


@pytest.mark.django_db
def test_filter_by_tag_and_city(client, search_url, sample_data):
    """
    Test filtering by 'tag' and 'city' returns
    only results containing provided values.
    """
    response = client.get(search_url, {"tag": "pottery", "city": "Lviv"})
    assert response.status_code == 200

    results = response.data["results"]
    assert all(
        ("pottery" in item["tags"]) and (item["city"] == "Lviv")
        for item in results
    )


@pytest.mark.django_db
def test_search_pagination(client, search_url, sample_data):
    """
    Confirms that pagination returns a paginated structure.
    """
    response = client.get(search_url, {"page": 1, "page_size": 2})
    assert response.status_code == 200

    results = response.data
    assert "count" in results
    assert "next" in results
    assert "previous" in results
    assert "results" in results

    assert results["next"] is not None
    assert results["results"] is not None


@pytest.mark.django_db
def test_default_ordering(client, search_url, sample_data):
    """
    Test that by default the results are ordered by '-created_at'.
    """
    response = client.get(search_url)
    assert response.status_code == 200

    results = response.data["results"]

    created_at_list = [
        r["created_at"] for r in results if "created_at" in r and r["created_at"]
    ]
    assert created_at_list == sorted(created_at_list, reverse=True)


@pytest.mark.django_db
def test_ordering_by_updated_at(client, search_url, sample_data):
    """
    Test setting ordering=updated_at sorts results
    ascending by updated_at field.
    """
    response = client.get(search_url, {"ordering": "updated_at"})
    assert response.status_code == 200

    results = response.data["results"]

    updated_at_list = [
        r["updated_at"] for r in results if "updated_at" in r and r["updated_at"]
    ]
    assert updated_at_list == sorted(updated_at_list, reverse=False)


@pytest.mark.django_db
def test_unsupported_filter_returns_empty(client, search_url, sample_data):
    """
    Test search returns no results when filtering by an unsupported field.
    """
    response = client.get(search_url, {"unknownfield": "value"})
    assert response.status_code == 200

    assert response.data["results"] == []
