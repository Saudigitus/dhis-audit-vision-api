from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session
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

def get_current_user_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:

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
