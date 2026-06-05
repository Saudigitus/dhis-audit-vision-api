import pytest

from core.dhis2 import dhis2_helpers
from core.dhis2.dhis2_helpers import (
    _timestamp_to_epoch,
    _validate_offset_hours,
    _validate_resource_uid,
    _validate_timestamp,
    get_resources_mapping,
)
from core.main import app


def _dependency_names(path: str, method: str) -> set[str]:
    route = next(route for route in app.routes if route.path == path and method in route.methods)
    return {dependency.call.__name__ for dependency in route.dependant.dependencies}


def test_audit_trigger_requires_superuser():
    assert "require_superuser" in _dependency_names("/api/runAudit", "POST")


def test_webhook_requires_authentication():
    assert "get_webhook_auth" in _dependency_names("/api/webhooks/dhis2/event", "POST")


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


def test_resource_mapping_falls_back_when_file_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(dhis2_helpers, "DATA_BASE_DIR", str(tmp_path))

    mapping = get_resources_mapping()

    assert mapping["org.hisp.dhis.program.Program"]["endpoint"] == "programs"


def test_resource_mapping_file_overrides_default(monkeypatch, tmp_path):
    mapping_dir = tmp_path / "data"
    mapping_dir.mkdir()
    mapping_file = mapping_dir / "klass_resource_mapping.json"
    mapping_file.write_text(
        '{"org.hisp.dhis.program.Program": {"endpoint": "customPrograms"}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(dhis2_helpers, "DATA_BASE_DIR", str(mapping_dir))

    mapping = get_resources_mapping()

    assert mapping["org.hisp.dhis.program.Program"]["endpoint"] == "customPrograms"
