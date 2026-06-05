from secrets import compare_digest

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from fastapi.security.utils import get_authorization_scheme_param
from jwt import ExpiredSignatureError, InvalidTokenError
import requests
from sqlalchemy.orm import Session
from core.common.config import get_dhis2_tls_verify
from core.config import settings
from core.db.dependencies import get_db
from core.auth.security import verify_password, decode_token
from core.auth.models import User
import core.auth.crud as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)


def _unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _require_active(user: User | None) -> User:
    if not user:
        raise _unauthorized()
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


# --- Bearer Token ---

def _get_user_from_token(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise _unauthorized()
        user = user_crud.get_by_username(db, username)
        if not user:
            raise _unauthorized()
        return user
    except ExpiredSignatureError as exc:
        raise _unauthorized("Token expired") from exc
    except InvalidTokenError as exc:
        raise _unauthorized("Invalid token") from exc


def get_current_user_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    return _get_user_from_token(token, db)


# --- DHIS2 ApiToken Auth ---

def _api_token_from_request(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "apitoken":
        return None
    return token


def get_current_user_api_token(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = _api_token_from_request(request)
    return _get_user_from_token(token, db)


# --- Basic Auth ---

def get_current_user_basic(
    credentials: HTTPBasicCredentials = Depends(basic_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    user = user_crud.get_by_username(db, credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        return None
    return user


# --- Accept either Bearer OR Basic (DHIS2-style) ---

def get_current_user(
    token_user: User | None = Depends(get_current_user_token),
    api_token_user: User | None = Depends(get_current_user_api_token),
    basic_user: User | None = Depends(get_current_user_basic),
) -> User:
    user = token_user or api_token_user or basic_user
    return _require_active(user)


# --- Webhook guard ---

def _matches_webhook_api_token(token: str | None) -> bool:
    configured = settings.WEBHOOK_API_TOKEN
    if not token or configured is None:
        return False
    return compare_digest(token, configured.get_secret_value())


def _dhis2_accepts_api_token(token: str | None) -> bool:
    if not token:
        return False
    url = f"{settings.SERVER_DHIS2_URL.rstrip('/')}/api/me"
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"ApiToken {token}", "Accept": "application/json"},
            timeout=10,
            verify=get_dhis2_tls_verify(),
        )
    except requests.RequestException:
        return False
    return response.status_code == 200


def get_webhook_auth(
    request: Request,
    db: Session = Depends(get_db),
    token_user: User | None = Depends(get_current_user_token),
    basic_user: User | None = Depends(get_current_user_basic),
) -> User | None:
    user = token_user or basic_user
    if user:
        return _require_active(user)

    api_token = _api_token_from_request(request)
    if _matches_webhook_api_token(api_token):
        return None
    if _dhis2_accepts_api_token(api_token):
        return None

    return _require_active(_get_user_from_token(api_token, db))


# --- Superuser guard ---

def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")
    return current_user
