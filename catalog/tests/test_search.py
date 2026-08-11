"""Tests for browse search and pagination."""

import pytest

from catalog.models import Title

pytestmark = pytest.mark.django_db


def test_search_matches_the_description_too(client):
    Title.objects.create(
        name="Arrival", description="Linguists decode an alien language.", tmdb_id=1
    )
    Title.objects.create(name="Heat", description="A crew plans a bank job.", tmdb_id=2)
    response = client.get("/", {"q": "alien"})
    assert b"Arrival" in response.content
    assert b"Heat" not in response.content


def test_search_requires_every_word_to_match(client):
    Title.objects.create(name="The Dark Knight", tmdb_id=1)
    Title.objects.create(name="Knight of Cups", tmdb_id=2)
    response = client.get("/", {"q": "dark knight"})
    assert b"The Dark Knight" in response.content
    assert b"Knight of Cups" not in response.content


def test_search_words_can_match_across_name_and_description(client):
    Title.objects.create(
        name="Inception", description="A thief enters dreams.", tmdb_id=1
    )
    response = client.get("/", {"q": "inception dreams"})
    assert b"Inception" in response.content


def test_search_ignores_extra_whitespace(client):
    Title.objects.create(name="Dune", tmdb_id=1)
    response = client.get("/", {"q": "   dune   "})
    assert b"Dune" in response.content


def test_browse_paginates_long_lists(client):
    for i in range(30):
        Title.objects.create(name=f"Title {i:02d}", tmdb_id=i)
    response = client.get("/")
    assert response.status_code == 200
    assert len(response.context["titles"]) == 24
    assert response.context["page_obj"].has_next() is True


def test_second_page_shows_the_remainder(client):
    for i in range(30):
        Title.objects.create(name=f"Title {i:02d}", tmdb_id=i)
    response = client.get("/", {"page": "2"})
    assert len(response.context["titles"]) == 6
    assert response.context["page_obj"].has_previous() is True


def test_invalid_page_falls_back_to_the_first(client):
    for i in range(30):
        Title.objects.create(name=f"Title {i:02d}", tmdb_id=i)
    response = client.get("/", {"page": "not-a-number"})
    assert response.status_code == 200
    assert response.context["page_obj"].number == 1


def test_out_of_range_page_shows_the_last(client):
    for i in range(30):
        Title.objects.create(name=f"Title {i:02d}", tmdb_id=i)
    response = client.get("/", {"page": "99"})
    assert response.status_code == 200
    assert response.context["page_obj"].number == 2


def test_pagination_preserves_the_query(client):
    for i in range(30):
        Title.objects.create(name=f"Match {i:02d}", tmdb_id=i)
    response = client.get("/", {"q": "match", "page": "2"})
    assert response.context["page_obj"].number == 2
    assert b"q=match" in response.content
