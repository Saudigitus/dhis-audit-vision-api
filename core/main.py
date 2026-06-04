from fastapi import Depends, FastAPI, HTTPException
from core.routes.audit_object_urls import router as audit_object_router
from core.routes.audit_urls import router as audit_router
from core.routes.web_hook_urls import router as webhook_router
from core.auth.router import router as auth_router
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from core.audit.audit import AuditProcess
from core.notification.router import router as notification_router
from core.auth.dependencies import require_superuser
from core.auth.models import User
from pathlib import Path


app = FastAPI(title="FastAPI Project - DHIS2_AUDIT_VISION", version="1.0.0")

cors_origins = [origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if origin.strip()]
if "*" in cors_origins:
    raise RuntimeError("CORS_ALLOW_ORIGINS must list explicit origins; wildcard origins are not allowed")
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(audit_router, prefix="/api/audits", tags=["Audits"])
app.include_router(audit_object_router, prefix="/api/auditObjects", tags=["Audit Objects"])
app.include_router(webhook_router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    return {"message": "Welcome to the DHIS2 Audit Vision API!"}


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
def list_logs(_: User = Depends(require_superuser)):
    logs = os.listdir("logs")

    return {'logs': logs}


@app.get("/api/logs/{log}")
def get_log(log: str, _: User = Depends(require_superuser)):
    if not log.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid log name")
    log_path = Path("logs") / f"{log}.txt"
    with log_path.open("r") as f:
        log_data = json.loads(f.read())

    return log_data


@app.post("/api/runAudit")
def run_audit_manualy(_: User = Depends(require_superuser)):
    audit_process = AuditProcess()
    audit_process.run()
    return {"message": "Audit process completed successfully."}
