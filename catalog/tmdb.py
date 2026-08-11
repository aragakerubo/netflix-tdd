"""Import movie metadata from The Movie Database (TMDB).

fetch_movie performs the HTTP call. import_title maps a TMDB payload onto our
Title model. Keeping them separate lets the mapping be tested without the
network, by mocking fetch_movie.
"""

import os

import requests

from .models import Genre, Title

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def fetch_movie(tmdb_id):
    """Return TMDB's details payload for a movie by its numeric id."""
    api_key = os.environ.get("TMDB_API_KEY", "")
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    response = requests.get(url, params={"api_key": api_key}, timeout=10)
    response.raise_for_status()
    return response.json()


def _year_from(release_date):
    """Pull a four-digit year out of a TMDB release_date, or None."""
    prefix = (release_date or "")[:4]
    return int(prefix) if prefix.isdigit() else None


def import_title(tmdb_id):
    """Fetch a movie and create or update the matching Title.

    Idempotent on tmdb_id: importing the same movie twice updates the existing
    row rather than creating a duplicate.
    """
    data = fetch_movie(tmdb_id)

    vote = data.get("vote_average")
    title, _ = Title.objects.update_or_create(
        tmdb_id=data["id"],
        defaults={
            "name": data["title"],
            "description": data.get("overview", ""),
            "year": _year_from(data.get("release_date")),
            "runtime": data.get("runtime"),
            "rating": round(vote, 1) if vote is not None else None,
            "poster_path": data.get("poster_path") or "",
            "backdrop_path": data.get("backdrop_path") or "",
            "media_type": Title.MediaType.MOVIE,
        },
    )

    try:
        title.trailer_key = pick_trailer_key(fetch_movie_videos(data["id"]))
        title.save(update_fields=["trailer_key"])
    except Exception:
        # A missing or failing video list should not fail the whole import.
        pass

    genres = []
    for entry in data.get("genres", []):
        genre, _ = Genre.objects.get_or_create(name=entry["name"])
        genres.append(genre)
    title.genres.set(genres)

    return title


def fetch_popular_movies(page=1):
    """Return one page of TMDB's popular movies as summary objects."""
    api_key = os.environ.get("TMDB_API_KEY", "")
    url = f"{TMDB_BASE_URL}/movie/popular"
    response = requests.get(url, params={"api_key": api_key, "page": page}, timeout=10)
    response.raise_for_status()
    return response.json()["results"]


def populate_popular(pages=1):
    """Import popular movies from TMDB, one detail fetch per title.

    Reuses import_title, so it is idempotent on tmdb_id: re-running updates
    existing rows instead of creating duplicates. Returns the imported Titles.
    """
    imported = []
    for page in range(1, pages + 1):
        for summary in fetch_popular_movies(page):
            imported.append(import_title(summary["id"]))
    return imported


def fetch_movie_videos(tmdb_id):
    """Return TMDB's video list for a movie (trailers, teasers, clips)."""
    api_key = os.environ.get("TMDB_API_KEY", "")
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}/videos"
    response = requests.get(url, params={"api_key": api_key}, timeout=10)
    response.raise_for_status()
    return response.json().get("results", [])


def pick_trailer_key(videos):
    """Choose the best YouTube key from a TMDB video list.

    Prefers an official trailer, then any trailer, then any YouTube video.
    Returns an empty string when nothing usable is present.
    """
    youtube = [v for v in videos if v.get("site") == "YouTube" and v.get("key")]
    for predicate in (
        lambda v: v.get("type") == "Trailer" and v.get("official"),
        lambda v: v.get("type") == "Trailer",
        lambda v: True,
    ):
        for video in youtube:
            if predicate(video):
                return video["key"]
    return ""
