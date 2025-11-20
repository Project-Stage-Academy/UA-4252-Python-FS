from .settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_postgres",
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    },
    "mongodb": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "test_mongodb",
        "USER": os.environ.get("MONGO_INITDB_ROOT_USERNAME"),
        "PASSWORD": os.environ.get("MONGO_INITDB_ROOT_PASSWORD"),
        "HOST": os.environ.get("MONGO_HOST", "mongodb"),
        "PORT": os.environ.get("MONGO_PORT", 27017),
    }
}
