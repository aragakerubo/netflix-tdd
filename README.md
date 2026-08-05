# Reelflix

[![CI](https://github.com/aragakerubo/netflix-tdd/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/aragakerubo/netflix-tdd/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/aragakerubo/netflix-tdd/branch/main/graph/badge.svg)](https://codecov.io/gh/aragakerubo/netflix-tdd)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5.2%20LTS-092E20)

A Netflix-style catalog built test-first with Django 5.2 LTS, Postgres,
pytest, Playwright, Docker, and GitHub Actions.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

## Running the tests

```bash
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/netflix
export SECRET_KEY=dev DEBUG=1
pytest
```