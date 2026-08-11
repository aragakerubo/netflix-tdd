# Reelflix

[![CI](https://github.com/aragakerubo/netflix-tdd/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/aragakerubo/netflix-tdd/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/aragakerubo/netflix-tdd/branch/main/graph/badge.svg)](https://codecov.io/gh/aragakerubo/netflix-tdd)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5.2%20LTS-092E20)
![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20playwright-0A9EDC)

A Netflix-style streaming catalog built entirely test-first, following the chapter
structure of _Test-Driven Development with Django_ on a current stack.

Browse and search movies and TV shows imported from TMDB, watch trailers, save
titles to a personal watchlist, and read the whole catalog as JSON.

## Stack

| Layer         | Choice                        |
| ------------- | ----------------------------- |
| Framework     | Django 5.2 LTS on Python 3.12 |
| Database      | Postgres 16                   |
| API           | Django REST Framework 3.18    |
| Unit tests    | pytest + pytest-django        |
| Browser tests | Playwright                    |
| Local env     | Docker Compose                |
| CI            | GitHub Actions + Codecov      |
| Hosting       | Render (Docker)               |
| Metadata      | TMDB API                      |

## Quick start

```bash
git clone https://github.com/aragakerubo/netflix-tdd.git
cd netflix-tdd
cp .env.example .env        # then edit: set POSTGRES_PASSWORD and TMDB_API_KEY
docker compose up --build
```

The site is at http://localhost:8000. Seed it with real titles:

```bash
docker compose run --rm web python manage.py populate_catalog --pages 3 --media both
docker compose run --rm web python manage.py createsuperuser   # for the admin
```

## URLs

### Pages

| URL                     | Purpose                                         | Auth   |
| ----------------------- | ----------------------------------------------- | ------ |
| `/`                     | Browse grid, search, media filter, pagination   | Public |
| `/?q=matrix`            | Search by name or description                   | Public |
| `/?media=tv`            | Filter to movies or TV (`movie`, `tv`)          | Public |
| `/?page=2`              | Page through results                            | Public |
| `/titles/<slug>/`       | Title detail: synopsis, genres, runtime, rating | Public |
| `/titles/<slug>/watch/` | Embedded trailer player (404 without one)       | Public |
| `/genres/<slug>/`       | All titles in a genre                           | Public |
| `/watchlist/`           | My List                                         | Login  |
| `/accounts/signup/`     | Create an account                               | Public |
| `/accounts/login/`      | Log in                                          | Public |
| `/accounts/logout/`     | Log out (POST)                                  | Login  |
| `/admin/`               | Django admin                                    | Staff  |
| `/healthz/`             | Liveness probe, returns `{"status": "ok"}`      | Public |

### API

All API endpoints are read-only and require authentication.

| Endpoint                  | Returns                                    |
| ------------------------- | ------------------------------------------ |
| `POST /api/token/`        | Exchange username and password for a token |
| `GET /api/titles/`        | Paginated list of titles, 24 per page      |
| `GET /api/titles/<slug>/` | One title with its genres inline           |
| `GET /api/genres/`        | Paginated list of genres                   |
| `GET /api/genres/<slug>/` | One genre                                  |

## Using the API

Get a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -d "username=YOUR_USER&password=YOUR_PASSWORD"
```

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

Use it on every request:

```bash
curl http://localhost:8000/api/titles/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

```json
{
  "count": 120,
  "next": "http://localhost:8000/api/titles/?page=2",
  "previous": null,
  "results": [
    {
      "name": "The Matrix",
      "slug": "the-matrix",
      "description": "A hacker learns the truth about his reality.",
      "year": 1999,
      "media_type": "movie",
      "runtime": 136,
      "rating": "8.7",
      "poster_path": "/poster.jpg",
      "backdrop_path": "/backdrop.jpg",
      "tmdb_id": 603,
      "genres": [{ "name": "Action", "slug": "action" }]
    }
  ]
}
```

Without credentials the API returns `403`. In a browser, log in at
`/accounts/login/` and DRF's browsable interface works at any API URL.

## Testing

Inner-loop tests run on the host and need no browser:

```bash
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
set -a && source .env && set +a
pytest catalog
```

Functional tests run in the official Playwright image, so your host never needs
browser dependencies:

```bash
docker compose run --rm --build functional-tests
```

Coverage:

```bash
pytest catalog --cov --cov-report=term-missing
```

Settings live in `.coveragerc`; migrations, tests, and WSGI/ASGI boilerplate are
excluded so the number reflects code actually written.

## Management commands

| Command                                              | Purpose                               |
| ---------------------------------------------------- | ------------------------------------- |
| `populate_catalog --pages N --media movie\|tv\|both` | Bulk import from TMDB's popular lists |
| `import_title TMDB_ID`                               | Import one movie by its TMDB id       |
| `createsuperuser`                                    | Create an admin login                 |

Imports are idempotent on `tmdb_id`, so re-running refreshes existing titles
instead of duplicating them.

## Deployment

Hosted on Render from `render.yaml`, which provisions a Docker web service and a
managed Postgres.

1. Push to `main`.
2. In Render: **New** → **Blueprint** → point at this repo.
3. Paste `TMDB_API_KEY` when prompted.

Render supplies `DATABASE_URL`, generates `SECRET_KEY`, sets `DEBUG=0` and
`DJANGO_PRODUCTION=1`, and runs migrations at container start.

### Seeding production

There is no shell on Render's free plan, so seeding happens at container start:

| Variable            | Default | Purpose                                             |
| ------------------- | ------- | --------------------------------------------------- |
| `POPULATE_ON_START` | `0`     | Set to `1` for one deploy to seed, then back to `0` |
| `POPULATE_PAGES`    | `3`     | Pages to import, 20 titles each                     |
| `POPULATE_MEDIA`    | `both`  | `movie`, `tv`, or `both`                            |

Leaving `POPULATE_ON_START` on would not duplicate data, since imports are
idempotent, but it re-hits TMDB and slows every cold start.

### Self-hosting instead

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Runs gunicorn with `DEBUG=0` and the production security settings. The
`deploy.yml` workflow also publishes an image to `ghcr.io/aragakerubo/netflix-tdd`.

## Environment variables

| Variable                                              | Used by    | Notes                                                                        |
| ----------------------------------------------------- | ---------- | ---------------------------------------------------------------------------- |
| `SECRET_KEY`                                          | All        | Generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `DEBUG`                                               | All        | `1` locally, `0` in production                                               |
| `ALLOWED_HOSTS`                                       | All        | Comma-separated; Render adds its own host                                    |
| `DATABASE_URL`                                        | All        | Falls back to SQLite when unset                                              |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Compose    | Seed the local database container                                            |
| `TMDB_API_KEY`                                        | Imports    | From themoviedb.org; not needed for tests                                    |
| `DJANGO_PRODUCTION`                                   | Production | `1` enables HTTPS redirect, HSTS, secure cookies                             |
| `CSRF_TRUSTED_ORIGINS`                                | Production | Self-hosting only; Render derives it                                         |

Changing `POSTGRES_PASSWORD` after the volume exists requires
`docker compose down -v` to re-initialize.

## Architecture notes

- **Two test loops.** Fast inner-loop tests drive views and models through
  Django's test client; outer-loop Playwright tests drive a real browser.
- **Network never touched in tests.** TMDB calls are mocked; each fetch function
  has one test pinning the URL it builds.
- **Idempotent imports.** `update_or_create` on `tmdb_id` means re-running is
  always safe.
- **Search on the queryset.** `TitleQuerySet.search()` is the seam for swapping
  in Postgres full-text search later.
- **One grid partial.** `_title_grid.html` renders home, genre, and watchlist
  pages.

## Roadmap

- [ ] **Postgres full-text search** — stemming and relevance ranking; the
      queryset seam is already in place
- [ ] **Seasons and episodes** — shows are currently one row with an average
      episode runtime
- [ ] **Recommendations** — a "More like this" row from shared genres
- [ ] **Continue watching** — playback progress per user
- [ ] **User ratings** — alongside the TMDB score
- [ ] **Password reset** — needs an email backend (free tiers exist)
- [ ] **Unicode slugs** — non-Latin titles currently fall back to their TMDB id
- [ ] **API rate limiting** — DRF throttling
- [ ] **Query optimization** — `select_related` and indexes on filtered fields

## License

MIT
