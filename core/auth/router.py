from collections import defaultdict, deque
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from core.auth.schemas import UserCreate, UserRead, UserUpdate, TokenResponse
from core.auth.security import verify_password, create_access_token
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
import core.auth.crud as user_crud

router = APIRouter()

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW_SECONDS = 60
_login_attempts: dict[str, deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_login_rate_limit(request: Request) -> None:
    client_ip = _client_ip(request)
    now = monotonic()
    attempts = _login_attempts[client_ip]
    while attempts and now - attempts[0] >= LOGIN_RATE_WINDOW_SECONDS:
        attempts.popleft()
    if len(attempts) >= LOGIN_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many login attempts")
    attempts.append(now)


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _map_user_crud_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, user_crud.UserAlreadyExistsError):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, user_crud.UserNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))


# --- Login ---

@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    enforce_login_rate_limit(request)
    user = user_crud.get_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise _invalid_credentials()
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


# --- Current user ---

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# --- User management (superuser only) ---

@router.post("/users", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    try:
        return user_crud.create(db, payload)
    except ValueError as exc:
        raise _map_user_crud_error(exc) from exc


@router.get("/users", response_model=list[UserRead])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    return user_crud.get_all(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    try:
        return user_crud.update(db, user_id, payload)
    except ValueError as exc:
        raise _map_user_crud_error(exc) from exc


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    try:
        user_crud.delete(db, user_id)
    except ValueError as exc:
        raise _map_user_crud_error(exc) from exc
    return {"message": "User deleted"}
