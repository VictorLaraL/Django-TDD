"""
Django command to wait the database to be available
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to wait the db """

    def handle(self, *args, **options):
        pass