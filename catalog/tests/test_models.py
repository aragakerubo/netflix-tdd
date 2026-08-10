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


def test_genre_str_and_slug(action):
    assert str(action) == "Action"
    assert action.slug == "action"


def test_genre_absolute_url_points_at_the_genre_page(action):
    assert action.get_absolute_url() == f"/genres/{action.slug}/"


def test_title_can_have_genres(matrix, action):
    matrix.genres.add(action)
    assert action in matrix.genres.all()
    assert matrix in action.titles.all()


def test_titles_with_the_same_name_get_distinct_slugs(db):
    first = Title.objects.create(name="The Odyssey", tmdb_id=1)
    second = Title.objects.create(name="The Odyssey", tmdb_id=2)
    assert first.slug == "the-odyssey"
    assert second.slug != first.slug
    assert second.slug.startswith("the-odyssey")


def test_non_latin_name_still_gets_a_usable_slug(db):
    title = Title.objects.create(name="君の名は", tmdb_id=372058)
    assert title.slug != ""
    assert title.get_absolute_url() == f"/titles/{title.slug}/"
