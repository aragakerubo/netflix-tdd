"""Inner-loop tests for the catalog views."""

import pytest

from catalog.models import Title

pytestmark = pytest.mark.django_db


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_shows_the_brand(client):
    response = client.get("/")
    assert b"Reelflix" in response.content


def test_home_page_has_a_search_box(client):
    response = client.get("/")
    assert b'placeholder="Search titles"' in response.content


def test_home_lists_all_titles_without_a_query(client):
    Title.objects.create(name="The Matrix", year=1999)
    Title.objects.create(name="Inception", year=2010)
    response = client.get("/")
    assert b"The Matrix" in response.content
    assert b"Inception" in response.content


def test_search_filters_titles_by_name(client):
    Title.objects.create(name="The Matrix", year=1999)
    Title.objects.create(name="Inception", year=2010)
    response = client.get("/", {"q": "matrix"})
    assert b"The Matrix" in response.content
    assert b"Inception" not in response.content


def test_search_with_no_matches_shows_a_message(client):
    Title.objects.create(name="The Matrix", year=1999)
    response = client.get("/", {"q": "zzzzz"})
    assert b"No titles found" in response.content
