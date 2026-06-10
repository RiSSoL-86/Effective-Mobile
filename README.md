# Effective Mobile — Backend

Django + [django-modern-rest](https://pypi.org/project/django-modern-rest/) async API service.

## Requirements

- Python 3.12
- [Pipenv](https://pipenv.pypa.io/)
- Docker + Docker Compose
- `make` — preinstalled on Linux/macOS; on Windows install via
  [Chocolatey](https://chocolatey.org/) (`choco install make`) or
  [Scoop](https://scoop.sh/) (`scoop install make`). Or just run the raw
  commands from the `Makefile` directly.

## Local setup

```bash
# 1. Install make (it drives every command below)
#    Linux/macOS — preinstalled
#    Windows     — choco install make   (or: scoop install make)

# 2. Install dependencies (incl. dev) and the virtualenv
pipenv install --dev

# 3. Install git hooks
make pre-commit.install
```

### Spin up dependencies (PostgreSQL + Redis)

The Postgres container uses an **external** volume, so create it once:

```bash
docker volume create db_data
```

Provide the database credentials in the environment (a `.env` file in the
project root is picked up by Docker Compose automatically). They must match
the `[database]` section of `src/config.toml`:

```dotenv
POSTGRES_DB=db1
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pass
```

Then start the services:

```bash
make compose.deps.dev          # up -d
# make compose.deps.dev.down   # to stop them
```

### Run the project

```bash
make migrate          # apply database migrations
make createsuperuser  # create an admin account
make run              # start the dev server on http://localhost:8000
```

## URLs

| Resource    | URL                                  |
|-------------|--------------------------------------|
| Admin panel | http://localhost:8000/admin/         |
| Swagger UI  | http://localhost:8000/api/docs/      |
| OpenAPI JSON| http://localhost:8000/api/schema.json |

## Useful commands

```bash
make lint   # ruff format + ruff check --fix + mypy
make test   # pytest
```
