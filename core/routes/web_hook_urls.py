from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from core.audit.service import extract_resource_uid_from_event_path, process_dhis2_event_safe
import json

router = APIRouter()

class Dhis2EventWebhook(BaseModel):
    model_config = ConfigDict(extra="ignore")
    path: str
    created_at: datetime = Field(alias="createdAt")

@router.post("/dhis2/event", status_code=status.HTTP_202_ACCEPTED)
async def receive_dhis2_event_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    try:
        data = json.loads(body)
        payload = Dhis2EventWebhook(**data)
        resource_uid = extract_resource_uid_from_event_path(payload.path)
        background_tasks.add_task(process_dhis2_event_safe, resource_uid, payload.created_at)
        return {
            "status": "accepted",
            "message": "Webhook received and queued for processing"
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process webhook")