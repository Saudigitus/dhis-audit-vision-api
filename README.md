# DHIS2_AUDIT_VISION

Project for implementing DHIS2 audit visualization.

## Running with Docker

### 1. Configure the environment variables

Create the `.env` file and replace the required example values:

```sh
cp .env.example .env
```

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

This command creates the configured admin user if it does not exist and prints
a new access token every time it runs.

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

This command creates the configured admin user if it does not exist and prints
a new access token every time it runs.

### 6. Start the server
```sh
python runserver.py
```
