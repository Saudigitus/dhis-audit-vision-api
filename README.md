# DHIS2 Audit Vision

## Overview

`DHIS2_Audit_Vision` is a FastAPI-based project for visualizing DHIS2 audit data and integrating audit operations with xAPI-style workflows. It provides authentication, audit processing, webhook handling, notification delivery, and administrative utilities for database seeding and manual audit execution.

## Key Features

- REST API powered by FastAPI
- Database migrations with Alembic
- PostgreSQL database support via SQLAlchemy and `psycopg2`
- Authentication and role management
- Audit processing endpoints and scheduled audit execution
- Webhook and notification route support
- Environment configuration via `.env`

## Tech Stack

- Python 3.x
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic / Pydantic Settings
- Typer CLI
- python-dotenv

## Prerequisites

- Python 3.11+ installed
- PostgreSQL instance available
- Git client if cloning the repository

## Installation

1. Open a terminal in the project root.
2. Create the virtual environment:

```powershell
python -m venv .venv
```

3. Activate the virtual environment:

```powershell
. .venv\Scripts\Activate.ps1
```

or for CMD:

```cmd
.venv\Scripts\activate.bat
```

4. Install project dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the repository root and set the required environment variables.

Use `.env.example` as a template and update values before running the application.

Example `.env` values:

```dotenv
DB_HOST=db
DB_PORT=5432
DB_NAME=dhis_audit
DB_USER=audit_user
DB_PASSWORD=changeme
ENVIRONMENT=development
host=0.0.0.0
port=8000
SERVER_DHIS2_URL=
SERVER_DHIS2_AUTH=
SQL_VIEW_ID=
CONTROL_FILE_PATH=./data/control_file.json
DATA_BASE_DIR=./data
SECRET_KEY=your_secret_key_here
TOKEN_EXPIRE_MINUTES=30
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=password
OFFSET_HOURS=0
RETRIEVE_SQL_VIEW_ID=
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
```

> The application depends on many configuration values. Make sure the `.env` file contains valid values for all required settings before starting the app.

## Docker Deployment

The project includes Docker support to run the FastAPI application together with PostgreSQL.

1. Copy the example env file:

```bash
cp .env.example .env
```

2. Update `.env` with real values and set `DB_HOST=db` for Docker Compose.

3. Build and start the services:

```bash
docker compose up --build
```

4. Open the application at `http://localhost:8000`.

5. Apply database migrations inside the running container:

```bash
docker compose exec web alembic upgrade head
```

6. Seed the default superuser:

```bash
docker compose exec web python commands.py seed-superuser
```

## Database Setup

The application uses Alembic for database migrations.

1. Generate migration files (optional, only if you change models):

```powershell
alembic revision --autogenerate -m "Create all tables"
```

2. Apply migrations:

```powershell
alembic upgrade head
```

## Data Seeding and CLI Tasks

The repository provides a CLI entrypoint via `commands.py`.

- Seed a default superuser:

```powershell
python commands.py seed-superuser
```

- Run audit process manually:

```powershell
python commands.py start-audit
```

## Run the Application

Start the server with the project entrypoint:

```powershell
python runserver.py
```

This launches Uvicorn and exposes the FastAPI application using the settings from `core.config`.

## API Endpoints

The application exposes these API groups:

- `/api/auth` – authentication and user management
- `/api/audits` – audit operations and audit listings
- `/api/auditObjects` – audit object endpoints
- `/api/webhooks` – webhook processing
- `/api/notifications` – notification delivery
- `/api/runAudit` – manual audit execution endpoint
- `/api/logs` – list and read log files

A root health endpoint is available at `/` and returns a welcome message.

## Recommended Workflow

1. Create and activate the virtual environment.
2. Install dependencies.
3. Create `.env` and populate database and service settings.
4. Run migrations with Alembic.
5. Seed the superuser and any initial data.
6. Start the server.
7. Use the API routes from the configured host and port.

## Project Structure

- `core/` – main application package
  - `auth/` – authentication, security and user management
  - `audit/` – audit processing services and helpers
  - `dhis2/` – DHIS2 integration helpers
  - `notification/` – notification endpoints and utilities
  - `routes/` – API route definitions
  - `db/` – database session and base classes
  - `schemas/` – Pydantic schemas
- `alembic/` – migration environment and revision history
- `commands.py` – CLI utility for seed and audit tasks
- `runserver.py` – local development server launcher
- `requirements.txt` – Python dependencies

## Notes

- Ensure PostgreSQL is running and reachable from the configured `DB_HOST` and `DB_PORT`.
- If you add or modify models, regenerate Alembic migrations and apply them.
- Use `python commands.py seed-superuser` after setting `ADMIN_*` values to ensure an admin account exists.


