"""User execute."""
# pylint: disable=E0401
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session
from db.models import User


def create_user(db: Session, user: User) -> User:
    """Create a new user."""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def check_user_exist(db: Session, username: str):
    """Get user by username."""
    if user := db.query(User).filter(User.username == username).first():
        return user
    return None


def get_user_by_id(db: Session, user_id: UUID):
    """Get user by user_id."""
    if user := db.query(User).filter(User.id == user_id).first():
        return user
    return None


def get_all_users(db: Session, offset: int = 0, limit: int = None):
    """Get all users with offset and limit."""
    query = db.query(User)
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()
