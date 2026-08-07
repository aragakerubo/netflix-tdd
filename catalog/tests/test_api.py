"""Tests for the read-only JSON API over the catalog."""

import pytest

pytestmark = pytest.mark.django_db


def test_titles_list_returns_json(client, matrix):
    response = client.get("/api/titles/")
    assert response.status_code == 200
    names = [t["name"] for t in response.json()["results"]]
    assert "The Matrix" in names


def test_title_detail_by_slug(client, matrix):
    response = client.get(f"/api/titles/{matrix.slug}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "The Matrix"
    assert data["year"] == 1999
    assert data["runtime"] == 136


def test_title_includes_its_genres(client, matrix, action):
    matrix.genres.add(action)
    response = client.get(f"/api/titles/{matrix.slug}/")
    assert [g["name"] for g in response.json()["genres"]] == ["Action"]


def test_genres_list_returns_json(client, action):
    response = client.get("/api/genres/")
    assert response.status_code == 200
    names = [g["name"] for g in response.json()["results"]]
    assert "Action" in names


def test_unknown_title_returns_404(client):
    response = client.get("/api/titles/does-not-exist/")
    assert response.status_code == 404
