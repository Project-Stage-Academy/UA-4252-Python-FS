from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from psycopg2 import connect, OperationalError as Psycopg2OpError
import time
import sys
import os


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        db_up = False
        retries_left = int(os.environ.get('MAX_DB_CONN_RETRIES', 30))
        sleep_time = int(os.environ.get('DB_WAIT_SLEEP', 1))

        while not db_up and retries_left:
            try:
                connect(
                    dbname=os.environ.get('POSTGRES_DB'),
                    user=os.environ.get('POSTGRES_USER'),
                    password=os.environ.get('POSTGRES_PASSWORD'),
                    host=os.environ.get('POSTGRES_HOST'),
                    port=os.environ.get('POSTGRES_PORT')
                )
                db_up = True
            except (Psycopg2OpError, OperationalError) as e:
                if 'database' in str(e) or 'db' in str(e):
                    self.stderr.write('Waiting for database to become available...\n')
                    retries_left -= 1
                    time.sleep(sleep_time)
                else:
                    raise

        if not retries_left:
            self.stdout.write('Database unavailable after waiting')
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('Database is available!'))
