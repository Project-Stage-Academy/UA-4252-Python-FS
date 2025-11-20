import os
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class Command(BaseCommand):
    """Django command to wait for MongoDB to become available."""

    def handle(self, *args, **options):
        retries_left = int(os.environ.get("MAX_MONGO_CONN_RETRIES", 30))
        sleep_time = int(os.environ.get("MONGO_WAIT_SLEEP", 1))

        mongo_settings = settings.DATABASES["mongodb"]

        client = MongoClient(
            host=mongo_settings["HOST"],
            port=int(mongo_settings["PORT"]),
            timeoutms=10,
        )

        while retries_left:
            try:
                client.admin.command("ping")  # does not require auth
                self.stdout.write(self.style.SUCCESS("MongoDB is available!"))
                client.close()
                return
            except (ConnectionFailure, ServerSelectionTimeoutError):
                self.stderr.write("Waiting for MongoDB to become available...\n")
                retries_left -= 1
                time.sleep(sleep_time)

        self.stdout.write(self.style.ERROR("MongoDB unavailable after waiting"))
        sys.exit(1)
