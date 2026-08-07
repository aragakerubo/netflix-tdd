"""Inner-loop tests for the catalog views."""

import pytest

from catalog.models import Title

pytestmark = pytest.mark.django_db


def test_pages_link_the_stylesheet(client):
    response = client.get("/")
    assert b"catalog/styles.css" in response.content


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


def test_detail_page_shows_title_information(client, matrix):
    response = client.get(matrix.get_absolute_url())
    assert response.status_code == 200
    assert b"The Matrix" in response.content
    assert b"A hacker learns the truth." in response.content
    assert b"1999" in response.content
    assert b"136" in response.content


def test_detail_page_returns_404_for_unknown_slug(client):
    response = client.get("/titles/does-not-exist/")
    assert response.status_code == 404


def test_home_links_each_title_to_its_detail_page(client, matrix):
    response = client.get("/")
    assert matrix.get_absolute_url().encode() in response.content


def test_genre_page_lists_titles_in_that_genre(client, matrix, action):
    matrix.genres.add(action)
    Title.objects.create(name="Inception", year=2010)
    response = client.get(action.get_absolute_url())
    assert response.status_code == 200
    assert b"The Matrix" in response.content
    assert b"Inception" not in response.content


def test_genre_page_returns_404_for_unknown_slug(client):
    response = client.get("/genres/does-not-exist/")
    assert response.status_code == 404


def test_detail_page_links_to_its_genres(client, matrix, action):
    matrix.genres.add(action)
    response = client.get(matrix.get_absolute_url())
    assert action.get_absolute_url().encode() in response.content
    assert b"Action" in response.content
