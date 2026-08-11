"""Tests for per-user watchlists."""

import pytest

from catalog.models import WatchlistItem

pytestmark = pytest.mark.django_db


def test_a_user_can_add_a_title_to_their_watchlist(user, matrix):
    item = WatchlistItem.objects.create(user=user, title=matrix)
    assert str(item) == f"{user.username}: {matrix.name}"
    assert matrix in user.watchlist_titles


def test_the_same_title_cannot_be_added_twice(user, matrix):
    from django.db import IntegrityError

    WatchlistItem.objects.create(user=user, title=matrix)
    with pytest.raises(IntegrityError):
        WatchlistItem.objects.create(user=user, title=matrix)


def test_watchlist_page_requires_login(client):
    response = client.get("/watchlist/")
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_watchlist_page_lists_saved_titles(client, user, matrix):
    WatchlistItem.objects.create(user=user, title=matrix)
    client.force_login(user)
    response = client.get("/watchlist/")
    assert response.status_code == 200
    assert b"The Matrix" in response.content


def test_adding_a_title_saves_it_and_redirects(client, user, matrix):
    client.force_login(user)
    response = client.post(f"/titles/{matrix.slug}/watchlist/add/")
    assert response.status_code == 302
    assert WatchlistItem.objects.filter(user=user, title=matrix).exists()


def test_adding_twice_is_harmless(client, user, matrix):
    client.force_login(user)
    client.post(f"/titles/{matrix.slug}/watchlist/add/")
    client.post(f"/titles/{matrix.slug}/watchlist/add/")
    assert WatchlistItem.objects.filter(user=user, title=matrix).count() == 1


def test_removing_a_title_deletes_it(client, user, matrix):
    WatchlistItem.objects.create(user=user, title=matrix)
    client.force_login(user)
    response = client.post(f"/titles/{matrix.slug}/watchlist/remove/")
    assert response.status_code == 302
    assert not WatchlistItem.objects.filter(user=user, title=matrix).exists()


def test_detail_page_offers_add_when_not_saved(client, user, matrix):
    client.force_login(user)
    response = client.get(matrix.get_absolute_url())
    assert b"Add to My List" in response.content


def test_detail_page_offers_remove_when_saved(client, user, matrix):
    WatchlistItem.objects.create(user=user, title=matrix)
    client.force_login(user)
    response = client.get(matrix.get_absolute_url())
    assert b"Remove from My List" in response.content
