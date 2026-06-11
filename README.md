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

## Auth flow

There are **two ways to obtain a token**:

- **Mobile API** (`/api/mobile/...`) — the app flow: device-bound + OTP, issues
  OAuth2 tokens tied to a specific device. This is what the client app uses.
- **OAuth2 endpoints** (`/oauth2/...`) — the raw OAuth2 token endpoint
  (`token/`, `revoke_token/`, `introspect/`, `swagger-token/`). Plain password
  grant by `client_id`/`secret`, no device/OTP. Used to authorize Swagger UI
  and for service-to-service integrations.

> Prerequisite: an OAuth2 **Application** (grant type `password`) must exist —
> create it in the admin panel. Its `client_id` is sent as the `CLIENT-ID`
> header to mobile auth endpoints.

### First-time registration (mobile)

1. **Init device** — `POST /api/mobile/devices/init/`
   headers `X-DEVICE-ID`, `FIREBASE-TOKEN`; body `osName, appVersion, osVersion,
   model, language`. → returns device `id` (UUID).
   *This UUID is the `DEVICE-ID` header for every call below.*
2. **Send OTP** — `POST /api/mobile/otp/send/`
   header `DEVICE-ID`; body `{ email }`. → returns `otpToken`.
   (`429` if a code is still active → use `/api/mobile/otp/resend/`.)
3. **Verify OTP** — `POST /api/mobile/otp/verify/`
   body `{ otpToken, code }`. → `{ verified: true }`. *(local/test code: `1111`)*
4. **Sign up** — `POST /api/mobile/auth/signup/`
   headers `DEVICE-ID` + `CLIENT-ID`; body `{ otpToken, firstName, lastName,
   password, passwordRepeat }`. → `{ email, accessToken, refreshToken }`.
   *(email is taken from the verified OTP, not the body)*

### Returning user

- **Sign in** — `POST /api/mobile/auth/signin/`
  headers `DEVICE-ID` + `CLIENT-ID`; body `{ email, password }`. → token pair.
  *(no OTP needed)*
- **Refresh** — `POST /api/mobile/auth/refresh/`
  header `DEVICE-ID`; body `{ refreshToken }`. → new pair (old refresh revoked).
- **Logout** — `POST /api/mobile/auth/logout/`
  `Authorization: Bearer <access>` + `DEVICE-ID`. → `204`, token revoked.

**Authenticated calls** send `Authorization: Bearer <accessToken>` **and** the
`DEVICE-ID` of the device the token was issued for — a mismatch returns `403`.

## Access summary

| Endpoint | Who | Otherwise |
|----------|-----|-----------|
| `devices/init`, `otp/*`, `auth/signup`, `auth/signin`, `auth/refresh` | anyone (device-bound, no login) | — |
| `auth/logout`, `users/me` (GET/PATCH/DELETE) | the authenticated user (self) | `401` without a valid token |
| `GET users/{id}` | **admin** or the **user themselves** | another user → `403`; missing id (admin) → `404` |
| `GET users/` (list all) | **admin only** | regular user → `403` |

> "Admin" = `is_staff = True`.

## Useful commands

```bash
make lint   # ruff format + ruff check --fix + mypy
make test   # pytest
```
