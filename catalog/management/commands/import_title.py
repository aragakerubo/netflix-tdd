"""Management command to import a movie from TMDB by its numeric id."""

from django.core.management.base import BaseCommand

from catalog import tmdb


class Command(BaseCommand):
    help = "Import a movie from TMDB by its numeric id."

    def add_arguments(self, parser):
        parser.add_argument("tmdb_id", type=int)

    def handle(self, *args, **options):
        title = tmdb.import_title(options["tmdb_id"])
        self.stdout.write(self.style.SUCCESS(f"Imported {title.name}"))
