import pytest

from catalog.models import Genre, Title


@pytest.fixture
def matrix(db):
    return Title.objects.create(
        name="The Matrix",
        year=1999,
        description="A hacker learns the truth.",
        runtime=136,
        rating="8.7",
    )


@pytest.fixture
def action(db):
    return Genre.objects.create(name="Action")


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="viewer", password="pass12345"
    )
