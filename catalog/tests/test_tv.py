"""Tests for importing TV shows from TMDB."""

from unittest.mock import patch

import pytest

from catalog import tmdb
from catalog.models import Title

pytestmark = pytest.mark.django_db

TV_SAMPLE = {
    "id": 1396,
    "name": "Breaking Bad",
    "overview": "A chemistry teacher turns to crime.",
    "first_air_date": "2008-01-20",
    "episode_run_time": [47],
    "vote_average": 8.9,
    "poster_path": "/bb-poster.jpg",
    "backdrop_path": "/bb-backdrop.jpg",
    "genres": [{"id": 18, "name": "Drama"}],
}


@patch("catalog.tmdb.fetch_tv")
def test_import_tv_maps_tv_specific_fields(mock_fetch):
    mock_fetch.return_value = TV_SAMPLE
    title = tmdb.import_tv(1396)
    assert title.name == "Breaking Bad"
    assert title.year == 2008
    assert title.runtime == 47
    assert title.media_type == "tv"
    assert title.tmdb_id == 1396


@patch("catalog.tmdb.fetch_tv")
def test_import_tv_handles_missing_runtime(mock_fetch):
    mock_fetch.return_value = {**TV_SAMPLE, "episode_run_time": []}
    title = tmdb.import_tv(1396)
    assert title.runtime is None


@patch("catalog.tmdb.fetch_tv")
def test_import_tv_is_idempotent(mock_fetch):
    mock_fetch.return_value = TV_SAMPLE
    tmdb.import_tv(1396)
    tmdb.import_tv(1396)
    assert Title.objects.filter(tmdb_id=1396).count() == 1


@patch("catalog.tmdb.requests.get")
def test_fetch_popular_tv_requests_the_tv_endpoint(mock_get):
    mock_get.return_value.json.return_value = {"results": [{"id": 1396}]}
    mock_get.return_value.raise_for_status.return_value = None
    results = tmdb.fetch_popular_tv(page=1)
    assert results == [{"id": 1396}]
    assert "/tv/popular" in mock_get.call_args[0][0]


@patch("catalog.tmdb.fetch_tv")
@patch("catalog.tmdb.fetch_popular_tv")
def test_populate_popular_tv_imports_each_show(mock_popular, mock_fetch):
    mock_popular.return_value = [{"id": 1396}, {"id": 1399}]
    mock_fetch.side_effect = lambda tid: {**TV_SAMPLE, "id": tid, "name": f"Show {tid}"}
    titles = tmdb.populate_popular_tv(pages=1)
    assert len(titles) == 2
    assert Title.objects.filter(media_type="tv").count() == 2


@patch("catalog.tmdb.fetch_tv")
@patch("catalog.tmdb.fetch_popular_tv")
def test_populate_command_accepts_a_tv_option(mock_popular, mock_fetch):
    from django.core.management import call_command

    mock_popular.return_value = [{"id": 1396}]
    mock_fetch.side_effect = lambda tid: {**TV_SAMPLE, "id": tid}
    call_command("populate_catalog", "--pages", "1", "--media", "tv")
    assert Title.objects.filter(tmdb_id=1396, media_type="tv").exists()


def test_detail_page_labels_a_show_as_tv(client):
    show = Title.objects.create(name="Breaking Bad", media_type="tv", tmdb_id=1396)
    response = client.get(show.get_absolute_url())
    assert b"TV Show" in response.content


def test_home_can_filter_to_movies_only(client):
    Title.objects.create(name="The Matrix", media_type="movie", tmdb_id=603)
    Title.objects.create(name="Breaking Bad", media_type="tv", tmdb_id=1396)
    response = client.get("/", {"media": "movie"})
    assert b"The Matrix" in response.content
    assert b"Breaking Bad" not in response.content


def test_home_can_filter_to_tv_only(client):
    Title.objects.create(name="The Matrix", media_type="movie", tmdb_id=603)
    Title.objects.create(name="Breaking Bad", media_type="tv", tmdb_id=1396)
    response = client.get("/", {"media": "tv"})
    assert b"Breaking Bad" in response.content
    assert b"The Matrix" not in response.content


def test_home_shows_both_by_default(client):
    Title.objects.create(name="The Matrix", media_type="movie", tmdb_id=603)
    Title.objects.create(name="Breaking Bad", media_type="tv", tmdb_id=1396)
    response = client.get("/")
    assert b"The Matrix" in response.content
    assert b"Breaking Bad" in response.content
