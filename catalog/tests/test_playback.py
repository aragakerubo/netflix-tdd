"""Tests for the trailer playback stub."""

from unittest.mock import patch

import pytest

from catalog import tmdb
from catalog.models import Title

pytestmark = pytest.mark.django_db

VIDEOS = {
    "results": [
        {"site": "YouTube", "type": "Teaser", "key": "teaser123", "official": True},
        {"site": "YouTube", "type": "Trailer", "key": "trailer456", "official": True},
    ]
}


def test_pick_trailer_key_prefers_youtube_trailer():
    assert tmdb.pick_trailer_key(VIDEOS["results"]) == "trailer456"


def test_pick_trailer_key_falls_back_to_any_youtube_video():
    only_teaser = [{"site": "YouTube", "type": "Teaser", "key": "teaser123"}]
    assert tmdb.pick_trailer_key(only_teaser) == "teaser123"


def test_pick_trailer_key_returns_empty_when_nothing_usable():
    assert (
        tmdb.pick_trailer_key([{"site": "Vimeo", "type": "Trailer", "key": "x"}]) == ""
    )


def test_title_has_trailer_reports_availability(matrix):
    assert matrix.has_trailer is False
    matrix.trailer_key = "trailer456"
    assert matrix.has_trailer is True


def test_watch_page_embeds_the_trailer(client, matrix):
    matrix.trailer_key = "trailer456"
    matrix.save()
    response = client.get(f"/titles/{matrix.slug}/watch/")
    assert response.status_code == 200
    assert b"youtube.com/embed/trailer456" in response.content


def test_watch_page_404s_without_a_trailer(client, matrix):
    response = client.get(f"/titles/{matrix.slug}/watch/")
    assert response.status_code == 404


def test_detail_page_links_to_watch_when_a_trailer_exists(client, matrix):
    matrix.trailer_key = "trailer456"
    matrix.save()
    response = client.get(matrix.get_absolute_url())
    assert b"/watch/" in response.content
