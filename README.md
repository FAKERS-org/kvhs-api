# KVHS API

FastAPI backend for the KVHS School Management and CMS platform.

This service provides APIs for:

- Authentication and role-based access
- Student, teacher, course, and enrollment management
- CMS content, document, and calendar management
- Search across CMS content

## API Details

- Project name: KVHS School Management & CMS API
- Current API version: 2.0.0
- Base URL (local): http://localhost:8000
- Versioned prefix: /api/v1
- API docs:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
  - OpenAPI JSON: http://localhost:8000/openapi.json

Health endpoints:

- `GET /`
- `GET /health`

## Tech Stack

- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy 2.x
- Alembic migrations
- Pydantic Settings
- JWT auth (`python-jose` + `passlib`)
- MinIO for document/object storage

## Project Structure

```text
kvhs-api/
	app/
		api/router.py            # API router composition
		core/                    # config, constants, middleware, security
		db/                      # engine/session/init
		models/                  # SQLAlchemy models
		repositories/            # data-access layer
		routes/                  # endpoint modules
		schemas/                 # request/response schemas
		services/                # business logic
		utils/                   # helpers
	alembic/                   # migrations
	tests/                     # tests
	test_cms.py                # manual end-to-end smoke script
```

## Quick Start (Local)

### 1. Install dependencies

This project is configured for `uv`.

```bash
uv sync
```

### 2. Configure environment variables

Create `.env` in `kvhs-api/` (or copy `.env.example`).

Required/important variables:

| Variable                      | Default                 | Notes                                       |
| ----------------------------- | ----------------------- | ------------------------------------------- |
| `DATABASE_URL`                | `sqlite:///./school.db` | Use PostgreSQL for non-trivial environments |
| `AUTO_CREATE_TABLES`          | `true`                  | Auto-creates tables on startup when true    |
| `SECRET_KEY`                  | development default     | Change in production                        |
| `ALGORITHM`                   | `HS256`                 | JWT signing algorithm                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                    | Access token TTL                            |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                     | Refresh token TTL                           |
| `ALLOWED_ORIGINS`             | localhost frontends     | Comma-separated origins                     |
| `UPLOAD_DIR`                  | `./uploads`             | Local upload directory                      |
| `MAX_UPLOAD_SIZE`             | `10485760`              | 10MB                                        |
| `MINIO_ENDPOINT`              | `localhost:9000`        | MinIO endpoint                              |
| `MINIO_ACCESS_KEY`            | `minioadmin`            | MinIO access key                            |
| `MINIO_SECRET_KEY`            | `minioadmin`            | MinIO secret key                            |
| `MINIO_BUCKET_NAME`           | `kvhs-files`            | MinIO bucket name                           |
| `MINIO_SECURE`                | `false`                 | Use TLS for MinIO                           |

### 3. Run the API

```bash
uv run uvicorn app.main:app --reload
```

The app starts on http://localhost:8000.

## Route Groups

All route groups are available both:

- without prefix (for backward compatibility)
- with `/api/v1` prefix (recommended)

Example: both `/auth/login` and `/api/v1/auth/login` are valid.

Main groups:

- `/auth` - register, login, token, current user profile
- `/students` - CRUD students
- `/teachers` - CRUD teachers
- `/courses` - CRUD courses
- `/enrollments` - CRUD enrollments
- `/content` - CMS content CRUD + publish/unpublish
- `/documents` - document upload/CRUD
- `/calendar` - calendar event CRUD
- `/cms` - departments and tags
- `/search` - content search

## Authentication and Authorization

Auth uses JWT Bearer tokens.

Core role behavior:

- First admin can register without auth if no admin exists.
- Admin/staff can register teachers and students.
- Teachers/admins can create and manage content.
- Students can only access published content.

Typical flow:

1. Register admin: `POST /api/v1/auth/register/admin`
2. Login: `POST /api/v1/auth/login`
3. Use `Authorization: Bearer <access_token>`
4. Verify current user: `GET /api/v1/auth/me`

## Database and Migrations

The app can auto-create tables (`AUTO_CREATE_TABLES=true`) and also supports Alembic migrations.

Run migrations:

```bash
uv run alembic upgrade head
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe_change"
```

## Docker

### Local DB stack (from workspace root)

`docker-compose.yml` in the workspace root starts:

- PostgreSQL (`localhost:5432`)
- pgAdmin (`http://localhost:5050`)

```bash
docker compose up -d
```

Then run the API from `kvhs-api/` with a PostgreSQL `DATABASE_URL`.

### API container image

The API `Dockerfile` runs migrations and starts Uvicorn:

```bash
docker build -t kvhs-api .
docker run --rm -p 8000:8000 --env-file .env kvhs-api
```

## Testing

Run automated tests:

```bash
uv run python -m unittest tests/test_app_improvements.py
```

Optional manual smoke test script:

```bash
uv run python test_cms.py
```

## Deployment Notes

`render.yaml` is included for Render deployment with:

- Docker runtime
- managed database
- generated `SECRET_KEY`

Set production-safe values for:

- `SECRET_KEY`
- `ALLOWED_ORIGINS`
- `DATABASE_URL`
- Cloudinary credentials (if document uploads are enabled)

## Related Docs

- `API_ARCHITECTURE.md`
- `CMS_README.md`
- `REFACTORING_GUIDE.md`
- `IMPLEMENTATION_SUMMARY.md`
