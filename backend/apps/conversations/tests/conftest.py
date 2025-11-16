import pytest
from django.conf import settings
from pymongo import MongoClient


@pytest.fixture(autouse=True, scope="session")
def clean_test_mongo():
    """Clean MongoDB test database before and after the test session."""

    mongo_settings = settings.DATABASES["mongodb"]

    client = MongoClient(
        host=mongo_settings["HOST"],
        port=int(mongo_settings["PORT"]),
        username=mongo_settings.get("USER"),
        password=mongo_settings.get("PASSWORD"),
    )

    db_name = mongo_settings["NAME"]
    db = client[db_name]

    if not db.name.startswith("test"):
        raise RuntimeError(
            f"Refusing to clean non-test MongoDB database: {db.name}"
        )

    # Clean before tests
    client.drop_database(db_name)

    yield  # run tests

    # Clean after tests
    client.drop_database(db_name)
