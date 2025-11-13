import os
import sys
import time

from django.core.management import BaseCommand
from elasticsearch_dsl import connections, ElasticsearchDslException


class Command(BaseCommand):
    """Django command to wait for elasticsearch."""

    def handle(self, *args, **options):
        retries_left = int(os.environ.get("MAX_ES_CONN_RETRIES", 30))
        sleep_time = int(os.environ.get("ES_WAIT_SLEEP", 1))

        while retries_left:
            try:
                connection = connections.get_connection()
                if connection.ping():
                    self.stdout.write(self.style.SUCCESS("Elasticsearch is available!"))
                    return

            except (ElasticsearchDslException, KeyError):
                pass

            self.stderr.write("Waiting for Elasticsearch to become available...\n")
            retries_left -= 1
            time.sleep(sleep_time)

        self.stdout.write(self.style.ERROR("Elasticsearch unavailable after waiting"))
        sys.exit(1)
