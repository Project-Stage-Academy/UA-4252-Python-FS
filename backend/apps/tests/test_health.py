import pytest

@pytest.mark.django_db
def test_health_check(client):
    """
    Ensure /api/health/ endpoint works and returns JSON with a 'status' key.
    """
    response = client.get("/api/health/")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "healthy", "running"]
