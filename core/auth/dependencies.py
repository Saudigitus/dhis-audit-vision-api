from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from core.auth.security import verify_password, decode_token
from core.auth.models import User
import core.auth.crud as user_crud

basic_scheme = HTTPBasic(auto_error=False)


def _extract_authorization_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        return None

    if scheme.lower() not in {"bearer", "apitoken"}:
        return None

    token = token.strip()
    return token or None


def _require_active(user: User | None) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


# --- Bearer / DHIS2 ApiToken ---

def get_current_user_token(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:

    token = _extract_authorization_token(authorization)
    if not token:
        return None
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        user = user_crud.get_by_username(db, username)
        return user
    except Exception:
        return None


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
    basic_user: User | None = Depends(get_current_user_basic),
) -> User:
    user = token_user or basic_user
    return _require_active(user)


# --- Superuser guard ---

def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")
    return current_user
