from fastapi import Depends, FastAPI, HTTPException, Request
from starlette import status
from core.routes.audit_object_urls import router as audit_object_router
from core.routes.audit_urls import router as audit_router
from core.routes.web_hook_urls import router as webhook_router
from core.auth.router import router as auth_router
import json
import re
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.audit.audit import AuditProcess
from core.notification.router import router as notification_router
from core.auth.dependencies import require_superuser
from core.auth.models import User
from pathlib import Path
from core.config import settings


LOG_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+(?:\.txt|\.log)?$")
LOG_DIR = Path("logs")


is_production = settings.ENVIRONMENT.lower() == "production"
app = FastAPI(
    title="FastAPI Project - DHIS2_AUDIT_VISION",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

cors_origins = settings.cors_allow_origins
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


@app.middleware("http")
async def reject_large_request_bodies(request: Request, call_next):
    content_length = request.headers.get("content-length")
    try:
        request_size = int(content_length) if content_length else 0
    except ValueError:
        return JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)
    if request_size > settings.MAX_REQUEST_BODY_BYTES:
        return JSONResponse(
            {"detail": "Request body too large"},
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )
    return await call_next(request)


app.include_router(audit_router, prefix="/api/audits", tags=["Audits"])
app.include_router(audit_object_router, prefix="/api/auditObjects", tags=["Audit Objects"])
app.include_router(webhook_router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    return {"message": "Welcome to the DHIS2 Audit Vision API!"}


@app.get("/api/endpoints/")
def list_endpoints(_: User = Depends(require_superuser)):
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
    LOG_DIR.mkdir(exist_ok=True)
    logs = [
        entry.name
        for entry in LOG_DIR.iterdir()
        if entry.is_file() and entry.suffix in {".txt", ".log"}
    ]
    return {'logs': logs}


@app.get("/api/logs/{log}")
def get_log(log: str, _: User = Depends(require_superuser)):
    if not LOG_NAME_PATTERN.fullmatch(log):
        raise HTTPException(status_code=400, detail="Invalid log name")
    log_path = LOG_DIR / log
    if not log_path.suffix:
        log_path = log_path.with_suffix(".txt")
    if not log_path.exists() or not log_path.is_file():
        raise HTTPException(status_code=404, detail="Log not found")

    file_size = log_path.stat().st_size
    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        if file_size > settings.LOG_MAX_BYTES:
            f.seek(max(file_size - settings.LOG_MAX_BYTES, 0))
            return {
                "truncated": True,
                "bytes": settings.LOG_MAX_BYTES,
                "content": f.read(),
            }
        content = f.read()

    try:
        log_data = json.loads(content)
    except json.JSONDecodeError:
        log_data = {"truncated": False, "content": content}

    return log_data


@app.post("/api/runAudit")
def run_audit_manualy(_: User = Depends(require_superuser)):
    audit_process = AuditProcess()
    audit_process.run()
    return {"message": "Audit process completed successfully."}