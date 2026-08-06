"""Inner-loop tests for the catalog admin registration."""

import pytest
from django.contrib import admin as django_admin

from catalog.models import Genre, Title

pytestmark = pytest.mark.django_db


def test_title_is_registered_in_admin():
    assert django_admin.site.is_registered(Title)


def test_genre_is_registered_in_admin():
    assert django_admin.site.is_registered(Genre)


def test_staff_can_view_the_title_changelist(client, django_user_model, matrix):
    admin_user = django_user_model.objects.create_superuser(
        username="admin", password="pass12345"
    )
    client.force_login(admin_user)
    response = client.get("/admin/catalog/title/")
    assert response.status_code == 200
    assert b"The Matrix" in response.content
