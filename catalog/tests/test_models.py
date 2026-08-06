"""Tests for the Title model."""

import pytest

from catalog.models import Title

pytestmark = pytest.mark.django_db


def test_title_str_is_its_name():
    title = Title.objects.create(name="The Matrix", year=1999)
    assert str(title) == "The Matrix"


def test_slug_is_generated_from_the_name():
    title = Title.objects.create(name="The Matrix Reloaded", year=2003)
    assert title.slug == "the-matrix-reloaded"


def test_tmdb_fields_default_to_empty():
    title = Title.objects.create(name="Local Indie Film")
    assert title.tmdb_id is None
    assert title.poster_path == ""
    assert title.rating is None
    assert title.media_type == "movie"


def test_get_absolute_url_points_at_the_detail_page(matrix):
    assert matrix.get_absolute_url() == f"/titles/{matrix.slug}/"
