from core.config import settings


def get_required_env(name: str) -> str:
    value = getattr(settings, name, None)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not configured")
    if hasattr(value, "get_secret_value"):
        return value.get_secret_value()
    return value


def get_dhis2_tls_verify() -> bool | str:
    return settings.DHIS2_CA_BUNDLE or True
