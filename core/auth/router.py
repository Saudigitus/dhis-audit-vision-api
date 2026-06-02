from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from core.auth.schemas import UserCreate, UserRead, UserUpdate, TokenResponse
from core.auth.security import verify_password, create_access_token
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
import core.auth.crud as user_crud

router = APIRouter()

# --- Login ---

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
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
    return user_crud.create(db, payload)


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
    return user_crud.get_by_id(db, user_id)


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    return user_crud.update(db, user_id, payload)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_superuser),
):
    user_crud.delete(db, user_id)
    return {"message": "User deleted"}
