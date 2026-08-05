from django.db import models
from django.utils.text import slugify


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

    # Populated from TMDB later. Nullable/blank so admin-created titles work now.
    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    runtime = models.PositiveIntegerField(null=True, blank=True, help_text="Minutes")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="TMDB vote average, 0-10",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
