from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:genre_detail", args=[self.slug])


class TitleQuerySet(models.QuerySet):
    """Query helpers for browsing the catalog."""

    def search(self, query):
        """Match titles whose name or description contains every search word.

        Requiring every word (rather than any) keeps multi-word searches
        specific: "dark knight" should not return everything with "knight".
        Matching the description as well as the name means a plot keyword
        finds a title even when the name does not contain it.
        """
        results = self
        for word in query.split():
            results = results.filter(
                Q(name__icontains=word) | Q(description__icontains=word)
            )
        return results


class Title(models.Model):
    """A movie or TV show in the catalog.

    Core fields (name, slug, description, year) cover admin-created content.
    The remaining fields mirror TMDB's payload so a later import chapter can
    populate them without changing the schema.
    """

    class MediaType(models.TextChoices):
        MOVIE = "movie", "Movie"
        TV = "tv", "TV Show"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    media_type = models.CharField(
        max_length=5,
        choices=MediaType.choices,
        default=MediaType.MOVIE,
    )
    genres = models.ManyToManyField(Genre, related_name="titles", blank=True)

    # Populated from TMDB later. Nullable/blank so admin-created titles work now.
    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    runtime = models.PositiveIntegerField(null=True, blank=True, help_text="Minutes")
    trailer_key = models.CharField(
        max_length=32,
        blank=True,
        help_text="YouTube video key for the trailer, from TMDB",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="TMDB vote average, 0-10",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TitleQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def _unique_slug(self):
        """Build a slug from the name, appending -2, -3, ... on collision.

        Title names are not unique (TMDB has several movies called
        "The Odyssey"), so slugify alone can violate the unique constraint.
        Names with no ASCII letters (many non-Latin titles) slugify to an empty
        string, which breaks URL reversing, so fall back to the tmdb_id.
        """
        base = slugify(self.name)
        if not base:
            base = str(self.tmdb_id) if self.tmdb_id else "title"
        slug = base
        counter = 2
        clashes = Title.objects.exclude(pk=self.pk)
        while clashes.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    @property
    def has_trailer(self):
        """True when a trailer is available to play."""
        return bool(self.trailer_key)

    def get_absolute_url(self):
        return reverse("catalog:title_detail", args=[self.slug])

    def get_watch_url(self):
        return reverse("catalog:title_watch", args=[self.slug])


class WatchlistItem(models.Model):
    """A title one user has saved to watch later.

    Unique per (user, title), so saving the same title twice is prevented at
    the database level rather than only in the view.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "title"], name="unique_watchlist_entry"
            )
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title.name}"
