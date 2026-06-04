import os

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not configured")
    return value


def get_dhis2_tls_verify() -> bool | str:
    return os.getenv("DHIS2_CA_BUNDLE") or True
