"""Repair any titles whose slug ended up empty (non-Latin names)."""

from django.db import migrations
from django.utils.text import slugify


def fix_empty_slugs(apps, schema_editor):
    Title = apps.get_model("catalog", "Title")
    for title in Title.objects.filter(slug=""):
        base = slugify(title.name) or (str(title.tmdb_id) if title.tmdb_id else "title")
        slug = base
        counter = 2
        while Title.objects.filter(slug=slug).exclude(pk=title.pk).exists():
            slug = f"{base}-{counter}"
            counter += 1
        title.slug = slug
        title.save(update_fields=["slug"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_genre_title_genres")]
    operations = [migrations.RunPython(fix_empty_slugs, noop)]
