"""Tests for user accounts: login page and signup."""

import pytest

pytestmark = pytest.mark.django_db


def test_login_page_loads(client):
    assert client.get("/accounts/login/").status_code == 200


def test_signup_creates_a_user_and_redirects(client, django_user_model):
    response = client.post(
        "/accounts/signup/",
        {
            "username": "newbie",
            "password1": "ver!complex-pass-123",
            "password2": "ver!complex-pass-123",
        },
    )
    assert response.status_code == 302
    assert django_user_model.objects.filter(username="newbie").exists()
