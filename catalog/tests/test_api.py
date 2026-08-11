"""Tests for the read-only JSON API, now behind authentication."""

import pytest

pytestmark = pytest.mark.django_db


def test_api_requires_authentication(client):
    response = client.get("/api/titles/")
    assert response.status_code == 403


def test_titles_list_returns_json(client, user, matrix):
    client.force_login(user)
    response = client.get("/api/titles/")
    assert response.status_code == 200
    names = [t["name"] for t in response.json()["results"]]
    assert "The Matrix" in names


def test_title_detail_by_slug(client, user, matrix):
    client.force_login(user)
    response = client.get(f"/api/titles/{matrix.slug}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "The Matrix"
    assert data["year"] == 1999
    assert data["runtime"] == 136


def test_title_includes_its_genres(client, user, matrix, action):
    matrix.genres.add(action)
    client.force_login(user)
    response = client.get(f"/api/titles/{matrix.slug}/")
    assert [g["name"] for g in response.json()["genres"]] == ["Action"]


def test_genres_list_returns_json(client, user, action):
    client.force_login(user)
    response = client.get("/api/genres/")
    assert response.status_code == 200
    names = [g["name"] for g in response.json()["results"]]
    assert "Action" in names


def test_unknown_title_returns_404(client, user):
    client.force_login(user)
    response = client.get("/api/titles/does-not-exist/")
    assert response.status_code == 404


def test_token_endpoint_issues_a_token(client, user):
    response = client.post(
        "/api/token/", {"username": "viewer", "password": "pass12345"}
    )
    assert response.status_code == 200
    assert response.json()["token"]
