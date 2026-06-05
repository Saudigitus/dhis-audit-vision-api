import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models.models import Audit, AuditObject
from core.common.enums.audit_enums import AuditType, AuditScope
from core.dhis2.dhis2_helpers import get_resource_objects_data, get_resources_mapping
from core.common.constants import constants
from core.utils.id_generator import generate_custom_id
from core.notification.models import NotificationConfig
from sqlalchemy import select
from core.notification.helpers import send_notification_email
from core.config import settings

SERVER_DHIS2_URL = settings.SERVER_DHIS2_URL
SERVER_DHIS2_AUTH = settings.SERVER_DHIS2_AUTH
BATCH_SIZE = 50


def chunk_list(data: List, size: int):
    """Yield successive chunks from list"""
    for i in range(0, len(data), size):
        yield data[i:i + size]


def parse_audit_row(headers: List[str], row: List) -> Audit:
    """Convert a row into an Audit model"""
    record = dict(zip(headers, row))

    # Parse attributes JSON safely
    attributes = None
    if record.get("attributes"):
        try:
            attributes = json.loads(record["attributes"])
        except Exception:
            attributes = None

    # Parse datetime
    created_at = None
    if record.get("createdat"):
        try:
            created_at = datetime.strptime(record["createdat"], "%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            created_at = None

    audit = Audit(
        id=generate_custom_id(),
        auditType=AuditType(record["audittype"]),
        auditScope=AuditScope(record["auditscope"]),
        klass=record["klass"],
        attributes=attributes,
        data=None,  # ignore invalid Java byte references
        createdBy=record["createdby"],
        uid=record.get("uid"),
        code=record.get("code"),
    )

    if created_at:
        audit.created_at = created_at

    return audit


def save_audit_json(db: Session, payload: Dict,  batch_size: int = BATCH_SIZE) -> Dict:
    """
    Generic function to save audit data from JSON into DB.
    Args:
        db: SQLAlchemy session
        payload: JSON payload (audit_data.json)
        batch_size: number of records per batch

    Returns:
        dict with stats
    """

    headers = [h["name"] for h in payload["listGrid"]["headers"]]
    rows = payload["listGrid"]["rows"]

    total, success, failed = len(rows), 0, 0

    for chunk in chunk_list(rows, batch_size):
        batch_objects = []

        for row in chunk:
            try:
                audit = parse_audit_row(headers, row)
                batch_objects.append(audit)
            except Exception:
                failed += 1

        try:
            if batch_objects:
                audit_objects = create_audit_objects_from_audit(batch_objects)
                db.add_all(batch_objects)
                db.add_all(audit_objects)
                db.commit()
                send_audit_notification(db, batch_objects)
                success += len(batch_objects)
        except SQLAlchemyError as e:
            db.rollback()
            failed += len(batch_objects)
            print("Database error:", str(e))
            if hasattr(e, "orig"):
                print("DB driver error:", e.orig)
            raise e

    print(f"Finished saving audits. Total: {total}, Success: {success}, Failed: {failed}")

    return {
        "total": total,
        "success": success,
        "failed": failed
    }


def create_audit_objects_from_audit(audits: list[Audit]) -> List[AuditObject]:
    """Create AuditObject models from an Audit model"""
    print("Creating AuditObjects from Audits...")
    mapping = get_resources_mapping()

    try:
        audit_objects = []
        audits_by_endpoint = defaultdict(list)
        for audit in audits:
            resource_endpoint = mapping.get(audit.klass or "", {}).get("endpoint")
            if resource_endpoint and audit.uid:
                audits_by_endpoint[resource_endpoint].append(audit)

        server = {"url": SERVER_DHIS2_URL, "auth": SERVER_DHIS2_AUTH,  "authType": constants.BASIC}
        resource_cache: dict[tuple[str, str], dict] = {}

        for resource_endpoint, endpoint_audits in audits_by_endpoint.items():
            object_data_by_id = get_resource_objects_data(
                server,
                resource_endpoint,
                [audit.uid for audit in endpoint_audits if audit.uid],
            )
            for resource_id, object_data in object_data_by_id.items():
                resource_cache[(resource_endpoint, resource_id)] = object_data

            for audit in endpoint_audits:
                object_data = resource_cache.get((resource_endpoint, audit.uid), {})
                audit_object = AuditObject(
                    auditId=audit.id,
                    objectId=audit.uid,
                    objectData=object_data,
                    auditScope=audit.auditScope,
                    auditType=audit.auditType,
                )
                audit_objects.append(audit_object)
        return audit_objects
    except Exception as e:
        print("Error creating AuditObjects")
        raise e


def save_audit_objects(db: Session, audit_objects: List[AuditObject], batch_size: int = BATCH_SIZE) -> Dict:
    """Persist audit objects only when called independently.

    save_audit_json persists Audit and AuditObject records in a single transaction.
    """

    total, success, failed = len(audit_objects), 0, 0

    for chunk in chunk_list(audit_objects, batch_size):
        try:
            db.bulk_save_objects(chunk)
            db.commit()
            print(f"Saved batch of {len(chunk)} AuditObjects")
            success += len(chunk)

        except SQLAlchemyError as e:
            db.rollback()
            failed += len(chunk)
            print("Database error:", str(e))
            if hasattr(e, "orig"):
                print("DB driver error:", e.orig)
            raise e
    print(f"Finished saving AuditObjects. Total: {total}, Success: {success}, Failed: {failed}")
    return {
        "total": total,
        "success": success,
        "failed": failed
    }


def send_audit_notification(db: Session, audits: List[Audit]):
    """Send notification based on audit data"""
    print("Checking for notifications to send based on audits...")
    for audit in audits:
        context = {
            "object": audit.uid,
            "type":   audit.klass.split(".")[-1] if audit.klass else None,
            "action": audit.auditType.value if audit.auditType else None,
            "user":   audit.createdBy,
            "time":   audit.created_at.strftime("%Y-%m-%d %H:%M") if audit.created_at else None,
        }
        query = select(NotificationConfig).where(
            NotificationConfig.action == context["action"],
            NotificationConfig.objectType == context["type"],
        ).order_by(NotificationConfig.created_at.desc()).limit(1)

        config = db.execute(query).scalar_one_or_none()

        print(f"Found notification config: {config} for audit {audit.id}")

        if config:
            send_notification_email(config=config, context=context)
