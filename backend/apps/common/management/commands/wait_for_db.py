from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Waiting for database to become available...')

        self.stdout.write(self.style.SUCCESS('Database is available!'))
