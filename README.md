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
authenticates only the webhook endpoint.

Deploy both DHIS2 SQL views and configure their IDs separately: `SQL_VIEW_ID`
must point to `dhis_query_view.sql` for scheduled polling, and
`RETRIEVE_SQL_VIEW_ID` must point to `dhis_retrieve_query_view.sql` for event
webhook processing. The webhook view receives `resource_uid`, `created_at`
formatted as `YYYY-MM-DD HH_MI_SS`, and the validated integer `offset_hours`.

### 2. Build and start the services (with DHIS2)

```sh
docker compose up --build -d
```

This will start:
- **Audit Vision API** at `http://localhost:8000` (docs at `http://localhost:8000/docs`)
- **Audit DB** (PostgreSQL)
- **DHIS2** at `http://localhost:8080` (default credentials: admin/district)
- **DHIS2 DB** (PostgreSQL with PostGIS)

Note: The first startup may take a few minutes as DHIS2 downloads and initializes the demo database.

### 2.1 Configure DHIS2 (dhis.conf)

O arquivo `dhis.conf` já está configurado com o sistema de auditoria ativado:
- `audit = METADATA, TRACKER, CREATE, UPDATE, DELETE`

Se precisar adicionar URLs permitidas para webhooks, edite o arquivo `dhis.conf` e adicione:
```
route.remote_servers_allowed = https://your-audit-api-url/
```

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
# View logs for specific services
docker compose logs -f api
docker compose logs -f dhis2-web

# Stop all services
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
