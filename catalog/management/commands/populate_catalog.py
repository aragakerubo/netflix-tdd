"""Populate the catalog with popular movies from TMDB."""

from django.core.management.base import BaseCommand

from catalog import tmdb


class Command(BaseCommand):
    help = "Populate the catalog with popular movies from TMDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pages",
            type=int,
            default=1,
            help="How many pages of popular movies to import (20 per page).",
        )

    def handle(self, *args, **options):
        titles = tmdb.populate_popular(pages=options["pages"])
        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(titles)} titles from TMDB")
        )
