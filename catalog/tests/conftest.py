import pytest

from catalog.models import Title


@pytest.fixture
def matrix(db):
    return Title.objects.create(
        name="The Matrix",
        year=1999,
        description="A hacker learns the truth.",
        runtime=136,
        rating="8.7",
    )
