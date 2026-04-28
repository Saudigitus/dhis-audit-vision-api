from fastapi import APIRouter, Request
import logging
from core.auth.dependencies import get_current_user, require_superuser
from fastapi import APIRouter, Depends
from core.auth.models import User
from core.audit.audit import AuditProcess
from dotenv import load_dotenv
import os

load_dotenv()

RETRIEVE_SQL_VIEW_ID = os.getenv("RETRIEVE_SQL_VIEW_ID", "aloNfrH2RGq")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/dhis2/event")
async def receive_dhis2_event_webhook(request: Request, _: User = Depends(require_superuser)):
    """
    Webhook endpoint to receive events from DHIS2.
    """
    try:
        audit_process = AuditProcess()

        payload = await request.json()
        logger.info(f"Received DHIS2 event webhook with payload: {payload}")
        print(f"Received DHIS2 webhook: {payload}")

        resource_uid = payload.get("path", "").split(".")[2]
        created_at = payload.get("createdAt")

        audit_process.automatic_run(RETRIEVE_SQL_VIEW_ID, resource_uid, created_at)

        return {
            "status": "success",
            "message": "Webhook received successfully"
        }

    except Exception:
        logger.exception("Error processing DHIS2 event webhook")
        return {
            "status": "error",
            "message": "Failed to process webhook"
        }
