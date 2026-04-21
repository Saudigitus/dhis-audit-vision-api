from fastapi import FastAPI
from core.routes.audit_object_urls import router as audit_object_router
from core.routes.audit_urls import router as audit_router
from core.auth.router import router as auth_router
import os
import json


app = FastAPI(title="FastAPI Project - DHIS2_AUDIT_VISION", version="1.0.0")

app.include_router(audit_router, prefix="/api/audits", tags=["Audits"])
app.include_router(audit_object_router, prefix="/api/auditObjects", tags=["Audit Objects"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Project - Integration of dhis2 and xAPI!"}


@app.get("/api/endpoints/")
def list_endpoints():
    endpoints = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name if hasattr(route, "name") else None,
                "tags": route.tags if hasattr(route, "tags") else []
            })
    return {"endpoints": endpoints}


@app.get("/api/logs")
def list_logs():
    logs = os.listdir("logs")

    return {'logs': logs}


@app.get("/api/logs/{log}")
def list_logs(log: str):

    log_data = None

    with open(f"logs/{log}.txt", "r") as f:
        log_data = json.loads(f.read())

    return log_data
