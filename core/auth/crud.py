from sqlalchemy.orm import Session
from sqlalchemy import select
from core.auth.models import User
from core.auth.schemas import UserCreate, UserUpdate
from core.auth.security import hash_password
import uuid


class UserAlreadyExistsError(ValueError):
    pass


class UserNotFoundError(ValueError):
    pass


def get_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def get_by_id(db: Session, user_id: str) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()


def create(db: Session, payload: UserCreate) -> User:
    if get_by_username(db, payload.username):
        raise UserAlreadyExistsError("Username already registered")
    if get_by_email(db, payload.email):
        raise UserAlreadyExistsError("Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_superuser=payload.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user_id: str, payload: UserUpdate) -> User:
    user = get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError("User not found")

    if payload.email:
        user.email = payload.email
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_superuser is not None:
        user.is_superuser = payload.is_superuser
    if payload.password:
        user.hashed_password = hash_password(payload.password)

    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user_id: str) -> None:
    user = get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError("User not found")
    db.delete(user)
    db.commit()
