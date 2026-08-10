"""Tests for the TMDB import, with the network mocked so they run offline."""

from unittest.mock import patch

import pytest

from catalog import tmdb
from catalog.models import Title

pytestmark = pytest.mark.django_db

SAMPLE = {
    "id": 603,
    "title": "The Matrix",
    "overview": "A hacker learns the truth.",
    "release_date": "1999-03-30",
    "runtime": 136,
    "vote_average": 8.7,
    "poster_path": "/poster.jpg",
    "backdrop_path": "/backdrop.jpg",
    "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
}


@patch("catalog.tmdb.fetch_movie")
def test_import_title_maps_tmdb_fields(mock_fetch):
    mock_fetch.return_value = SAMPLE
    title = tmdb.import_title(603)
    assert title.name == "The Matrix"
    assert title.tmdb_id == 603
    assert title.year == 1999
    assert title.runtime == 136
    assert float(title.rating) == 8.7
    assert title.poster_path == "/poster.jpg"
    assert title.media_type == "movie"


@patch("catalog.tmdb.fetch_movie")
def test_import_title_sets_genres(mock_fetch):
    mock_fetch.return_value = SAMPLE
    title = tmdb.import_title(603)
    names = set(title.genres.values_list("name", flat=True))
    assert names == {"Action", "Science Fiction"}


@patch("catalog.tmdb.fetch_movie")
def test_import_title_is_idempotent(mock_fetch):
    mock_fetch.return_value = SAMPLE
    tmdb.import_title(603)
    tmdb.import_title(603)
    assert Title.objects.filter(tmdb_id=603).count() == 1


@patch("catalog.tmdb.requests.get")
def test_fetch_movie_requests_the_right_endpoint(mock_get):
    mock_get.return_value.json.return_value = SAMPLE
    mock_get.return_value.raise_for_status.return_value = None
    data = tmdb.fetch_movie(603)
    assert data["title"] == "The Matrix"
    assert "/movie/603" in mock_get.call_args[0][0]


@patch("catalog.tmdb.fetch_movie")
def test_import_command_creates_the_title(mock_fetch):
    from django.core.management import call_command

    mock_fetch.return_value = SAMPLE
    call_command("import_title", "603")
    assert Title.objects.filter(tmdb_id=603).exists()


@patch("catalog.tmdb.requests.get")
def test_fetch_popular_movies_requests_popular_endpoint(mock_get):
    mock_get.return_value.json.return_value = {"results": [{"id": 603}]}
    mock_get.return_value.raise_for_status.return_value = None
    results = tmdb.fetch_popular_movies(page=2)
    assert results == [{"id": 603}]
    assert "/movie/popular" in mock_get.call_args[0][0]
    assert mock_get.call_args.kwargs["params"]["page"] == 2


@patch("catalog.tmdb.fetch_movie")
@patch("catalog.tmdb.fetch_popular_movies")
def test_populate_popular_imports_each_movie(mock_popular, mock_fetch):
    mock_popular.return_value = [{"id": 603}, {"id": 27205}]
    mock_fetch.side_effect = lambda tmdb_id: {
        **SAMPLE,
        "id": tmdb_id,
        "title": f"Movie {tmdb_id}",
    }
    titles = tmdb.populate_popular(pages=1)
    assert len(titles) == 2
    assert Title.objects.count() == 2


@patch("catalog.tmdb.fetch_movie")
@patch("catalog.tmdb.fetch_popular_movies")
def test_populate_command_creates_titles(mock_popular, mock_fetch):
    from django.core.management import call_command

    mock_popular.return_value = [{"id": 603}]
    mock_fetch.side_effect = lambda tmdb_id: {**SAMPLE, "id": tmdb_id}
    call_command("populate_catalog", "--pages", "1")
    assert Title.objects.filter(tmdb_id=603).exists()
