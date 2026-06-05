from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jwt import encode
from pydantic import SecretStr
from starlette.requests import Request

from core.audit import audit_helpers
from core.audit.service import extract_resource_uid_from_event_path
from core.auth import crud as user_crud
from core.auth import router as auth_router
from core.auth.dependencies import get_current_user_api_token, get_current_user_token, get_webhook_auth
from core.auth.security import ALGORITHM, SECRET_KEY, create_access_token, decode_token
from core.common.enums.audit_enums import AuditScope, AuditType
from core.config import settings
from core.models.models import Audit
from core.routes import audit_object_urls, audit_urls


class FakeDB:
    pass


def _dependency_names(path: str, method: str) -> set[str]:
    from core.main import app

    route = next(route for route in app.routes if route.path == path and method in route.methods)
    return {dependency.call.__name__ for dependency in route.dependant.dependencies}


def test_invalid_bearer_token_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_token(token="not-a-valid-token", db=FakeDB())

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token_is_rejected():
    token = encode(
        {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_token(token=token, db=FakeDB())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"


def test_access_token_round_trip():
    token = create_access_token({"sub": "admin"})

    assert decode_token(token)["sub"] == "admin"


def test_dhis2_api_token_scheme_accepts_api_jwt(monkeypatch):
    token = create_access_token({"sub": "admin"})
    request = Request(
        {
            "type": "http",
            "headers": [(b"authorization", f"ApiToken {token}".encode("ascii"))],
        }
    )

    class FakeUser:
        username = "admin"
        is_active = True

    monkeypatch.setattr(user_crud, "get_by_username", lambda db, username: FakeUser())

    assert get_current_user_api_token(request=request, db=FakeDB()).username == "admin"


def test_webhook_accepts_configured_static_api_token(monkeypatch):
    token = "abcdefghijklmnopqrstuvwxyz1234567890"
    monkeypatch.setattr(settings, "WEBHOOK_API_TOKEN", SecretStr(token))
    request = Request(
        {
            "type": "http",
            "headers": [(b"authorization", f"ApiToken {token}".encode("ascii"))],
        }
    )

    assert get_webhook_auth(request=request, db=FakeDB(), token_user=None, basic_user=None) is None


def test_webhook_accepts_dhis2_pat_when_dhis2_validates_it(monkeypatch):
    token = "d2pat_abcdefghijklmnopqrstuvwxyz1234567890"
    monkeypatch.setattr(settings, "WEBHOOK_API_TOKEN", None)
    request = Request(
        {
            "type": "http",
            "headers": [(b"authorization", f"ApiToken {token}".encode("ascii"))],
        }
    )

    class FakeResponse:
        status_code = 200

    def fake_get(url, headers, timeout, verify):
        assert url.endswith("/api/me")
        assert headers["Authorization"] == f"ApiToken {token}"
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr("core.auth.dependencies.requests.get", fake_get)

    assert get_webhook_auth(request=request, db=FakeDB(), token_user=None, basic_user=None) is None


@pytest.mark.parametrize("path", ["metadata.programs.Abcdef12345", "x.y.ZYXWVUT9876"])
def test_extract_resource_uid_from_event_path(path):
    assert len(extract_resource_uid_from_event_path(path)) == 11


def test_extract_resource_uid_rejects_invalid_path():
    with pytest.raises(ValueError):
        extract_resource_uid_from_event_path("metadata.only_two_parts")


def test_create_audit_objects_fetches_dhis2_data_in_batches(monkeypatch):
    calls = []

    def fake_mapping():
        return {"org.hisp.dhis.program.Program": {"endpoint": "programs"}}

    def fake_batch(server, resource, resource_ids, fields=None):
        calls.append((resource, sorted(resource_ids)))
        return {resource_id: {"id": resource_id, "displayName": resource_id} for resource_id in resource_ids}

    monkeypatch.setattr(audit_helpers, "get_resources_mapping", fake_mapping)
    monkeypatch.setattr(audit_helpers, "get_resource_objects_data", fake_batch)

    audits = [
        Audit(
            id="auditid001A",
            auditType=AuditType.CREATE,
            auditScope=AuditScope.METADATA,
            klass="org.hisp.dhis.program.Program",
            createdBy="admin",
            uid="Abcdef12345",
        ),
        Audit(
            id="auditid002B",
            auditType=AuditType.UPDATE,
            auditScope=AuditScope.METADATA,
            klass="org.hisp.dhis.program.Program",
            createdBy="admin",
            uid="ZYXWVUT9876",
        ),
    ]

    audit_objects = audit_helpers.create_audit_objects_from_audit(audits)

    assert calls == [("programs", ["Abcdef12345", "ZYXWVUT9876"])]
    assert [obj.objectId for obj in audit_objects] == ["Abcdef12345", "ZYXWVUT9876"]


def test_audit_write_routes_require_superuser():
    assert "require_superuser" in _dependency_names("/api/audits/create/", "POST")
    assert "require_superuser" in _dependency_names("/api/audits/{id}", "DELETE")
    assert "require_superuser" in _dependency_names("/api/auditObjects/create/", "POST")
    assert "require_superuser" in _dependency_names("/api/auditObjects/{id}", "DELETE")


def test_filter_allowlists_are_explicit():
    assert "uid" in audit_urls.AUDIT_FILTER_FIELDS
    assert "created_at" not in audit_urls.AUDIT_FILTER_FIELDS
    assert "auditId" in audit_object_urls.AUDIT_OBJECT_FILTER_FIELDS
    assert "created_at" not in audit_object_urls.AUDIT_OBJECT_FILTER_FIELDS


def test_login_rate_limit_rejects_after_limit():
    auth_router._login_attempts.clear()

    class Client:
        host = "203.0.113.10"

    class Request:
        headers = {}
        client = Client()

    request = Request()
    for _ in range(auth_router.LOGIN_RATE_LIMIT):
        auth_router.enforce_login_rate_limit(request)

    with pytest.raises(HTTPException) as exc_info:
        auth_router.enforce_login_rate_limit(request)

    assert exc_info.value.status_code == 429
