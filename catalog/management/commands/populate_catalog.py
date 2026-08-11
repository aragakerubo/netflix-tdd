"""Populate the catalog with popular movies or TV shows from TMDB."""

from django.core.management.base import BaseCommand

from catalog import tmdb


class Command(BaseCommand):
    help = "Populate the catalog with popular titles from TMDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pages",
            type=int,
            default=1,
            help="How many pages to import (20 titles per page).",
        )
        parser.add_argument(
            "--media",
            choices=["movie", "tv", "both"],
            default="movie",
            help="Which TMDB catalog to pull from.",
        )

    def handle(self, *args, **options):
        pages = options["pages"]
        media = options["media"]

        titles = []
        if media in ("movie", "both"):
            titles += tmdb.populate_popular(pages=pages)
        if media in ("tv", "both"):
            titles += tmdb.populate_popular_tv(pages=pages)

        self.stdout.write(
            self.style.SUCCESS(f"Imported {len(titles)} titles from TMDB")
        )
