# DHIS2_AUDIT_VISION

Project for implementing DHIS2 audit visualization.

## Running with Docker

### 1. Configure the environment variables

Create the `.env` file and replace the required example values:

```sh
cp .env.example .env
```

Set `SECRET_KEY` to a random value with at least 32 bytes. The API refuses to
start with an empty, weak, or documented placeholder key.

Set `CORS_ALLOW_ORIGINS` to the comma-separated browser origins that may call
the API. Wildcard origins are rejected. Set `MAX_REQUEST_BODY_BYTES` to the
largest request body the API should accept. If the DHIS2 server uses a private
CA, set `DHIS2_CA_BUNDLE` to its certificate bundle path.

Set `DHIS2_OBJECT_FIELDS` to the minimal DHIS2 fields that should be stored in
local audit object snapshots. Set `DHIS2_PROGRAM_DEPENDENCY_FIELDS` and
`DHIS2_DATASET_DEPENDENCY_FIELDS` to the fields used when resolving related
metadata IDs.

The DHIS2 webhook must send valid API credentials using one of these modes:
`http-basic`, `api-token`, or an explicit `Authorization: Bearer <token>`
header. For DHIS2 `api-token`, either configure a DHIS2 personal access token
for the event hook, which this API validates against `SERVER_DHIS2_URL/api/me`,
or set `WEBHOOK_API_TOKEN` to a high-entropy value with at least 32 bytes and
configure the same value in the DHIS2 event hook. `WEBHOOK_API_TOKEN`
authenticates only the webhook endpoint. Deploy the updated
`dhis_query_view.sql` definition in DHIS2 as well; it now receives the
validated integer variable `since_epoch`.

### 2. Build and start the services

```sh
docker compose up --build -d
```

The API will be available at `http://localhost:8000` and the interactive
documentation at `http://localhost:8000/docs`.

### 3. Run the migrations

```sh
docker compose exec api alembic upgrade head
```

To create a new migration:

```sh
docker compose exec api alembic revision --autogenerate -m "Migration description"
```

### 4. Create the superuser

```sh
docker compose exec api python commands.py seed-superuser
```

This command creates the configured admin user if it does not exist. It does
not print tokens by default; use `/api/auth/login` to obtain a token. If a
one-time bootstrap token is required, run it with `--print-token`.

### 5. View logs and stop the services

```sh
docker compose logs -f api
docker compose down
```

The PostgreSQL data, audit files, and logs are persisted in Docker volumes.

## Running locally

### 1. Create the virtual environment
```sh
python -m venv .venv
```

### 2. Activate the virtual environment

On Windows:

```sh
. .venv/Scripts/activate
```

### 3. Install the dependencies
```sh
pip install -r requirements.txt
```

For local test/development tooling:

```sh
pip install -r requirements-dev.txt
```

### 4. Configure the environment variables

Create the `.env` file in the project root from `.env.example`.

### 5. Run the database migrations

#### 5.1. Create a migration
```sh
alembic revision --autogenerate -m "Migration description"
```

#### 5.2. Apply the migrations
```sh
alembic upgrade head
```

#### 5.3. Create the superuser
```sh
python commands.py seed-superuser
```

This command creates the configured admin user if it does not exist. It does
not print tokens by default; use `/api/auth/login` to obtain a token. If a
one-time bootstrap token is required, run it with `--print-token`.

### 6. Start the server
```sh
python runserver.py
```
