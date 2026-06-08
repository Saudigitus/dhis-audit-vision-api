# DHIS2 Audit Vision - Docker Compose Files

This folder contains compose files for different deployment scenarios of DHIS2 Audit Vision.

## Available Scenarios

### 1. Scenario 1: Same Server
**Path**: `scenario-1-same-server/`

Use this scenario when:
- DHIS2 and the Audit API are on the same physical server
- The API is only accessible locally
- Nginx handles external access

**Configuration in .env**:
```env
SERVER_DHIS2_URL=http://localhost:8080
```

**EventHook URL in DHIS2**:
```
http://localhost:8000/api/webhooks/dhis2/event
```

---

### 2. Scenario 2: Different Servers
**Path**: `scenario-2-different-servers/`

Use this scenario when:
- DHIS2 and the Audit API are on separate servers
- Connection via public or private network

**Configuration in .env**:
```env
SERVER_DHIS2_URL=https://your-dhis2-instance-url
```

**EventHook URL in DHIS2**:
```
https://your-audit-api-domain/api/webhooks/dhis2/event
```

---

### 3. Scenario 3: Development / Testing
**Path**: `scenario-3-dev-docker-compose/`

Use this scenario when:
- You want to run everything (DHIS2, Database, API) in a single compose
- Ideal for development, testing, or evaluation

**Configuration in .env**:
```env
SERVER_DHIS2_URL=http://dhis2-web:8080
```

---

## How to Use

1. Choose the scenario that best fits your needs
2. Navigate to the scenario folder
3. Configure the `.env` file in the project root (the compose files are already set up to use `../../.env`)
4. Run:
   ```bash
   docker compose up --build -d
   ```
   
   Or explicitly specify the env file:
   ```bash
   docker compose --env-file ../../.env up --build -d
   ```

## Nginx Configs

Example Nginx configuration files are in the `nginx/` folder:

- `scenario-1-same-server.conf`: Restricts webhook to localhost
- `scenario-2-different-servers.conf`: Restricts webhook to the DHIS2 server IP

## Quick Start (Recommended for Dev)

For quick testing, use scenario 3:

```bash
cd docker/scenario-3-dev-docker-compose
docker compose --env-file ../../.env up --build -d
docker compose --env-file ../../.env exec api alembic upgrade head
docker compose --env-file ../../.env exec api python commands.py seed-superuser
```

The API will be available at `http://localhost:8000` and DHIS2 at `http://localhost:8080`.