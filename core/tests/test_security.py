import pytest

from core.auth.dependencies import _extract_authorization_token
from core.dhis2.dhis2_helpers import (
    _timestamp_to_epoch,
    _validate_offset_hours,
    _validate_resource_uid,
    _validate_timestamp,
)
from core.main import app


def _dependency_names(path: str, method: str) -> set[str]:
    route = next(route for route in app.routes if route.path == path and method in route.methods)
    return {dependency.call.__name__ for dependency in route.dependant.dependencies}


def test_audit_trigger_requires_superuser():
    assert "require_superuser" in _dependency_names("/api/runAudit", "POST")


def test_webhook_requires_authentication():
    assert "get_current_user" in _dependency_names("/api/webhooks/dhis2/event", "POST")


@pytest.mark.parametrize(
    ("authorization", "expected"),
    [
        ("Bearer jwt-token", "jwt-token"),
        ("ApiToken jwt-token", "jwt-token"),
        ("apitoken jwt-token", "jwt-token"),
        ("Basic abc123", None),
        ("jwt-token", None),
        ("Bearer   ", None),
        (None, None),
    ],
)
def test_authorization_token_accepts_bearer_and_dhis2_apitoken(authorization, expected):
    assert _extract_authorization_token(authorization) == expected


@pytest.mark.parametrize(
    ("validator", "value"),
    [
        (_validate_resource_uid, "abc'; DROP TABLE audit; --"),
        (_validate_timestamp, "2026-01-01 00_00_00'; SELECT pg_sleep(10); --"),
        (_validate_offset_hours, "2; DROP TABLE audit"),
        (_validate_offset_hours, -1),
        (_validate_offset_hours, 169),
    ],
)
def test_sql_view_parameters_reject_unsafe_values(validator, value):
    with pytest.raises(ValueError):
        validator(value)


def test_timestamp_is_converted_to_integer_epoch():
    assert _timestamp_to_epoch("2026-01-01 00_00_00") == 1767225600
