"""Paper group execute."""
# pylint: disable=E0401
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from db.models import PaperGroup
from db.execute.paper_group_info import delete_paper_group_info


def create_paper_group(db: Session, paper_group: PaperGroup) -> PaperGroup:
    """Create a paper group."""
    db.add(paper_group)
    db.commit()
    db.refresh(paper_group)
    return paper_group


def get_groups_by_user_id(db: Session, user_id: UUID):
    """Get paper groups by user_id."""
    if groups := db.query(PaperGroup).filter(PaperGroup.user_id == user_id).all():
        return groups


def get_group_by_id(db: Session, group_id: UUID):
    """Get paper group by id."""
    if group := db.query(PaperGroup).filter(PaperGroup.id == group_id).first():
        return group


def get_group_by_group_name(db: Session, group_name: str):
    """Get paper group by user_id."""
    if group := db.query(PaperGroup).filter(PaperGroup.group_name == group_name).first():
        return group


def get_groups_by_name_user_id(db: Session, group_name: str, user_id: UUID) -> PaperGroup:
    """Get paper group by group name, user_id."""
    if group := (
        db.query(PaperGroup)
        .filter(PaperGroup.user_id == user_id)
        .filter(PaperGroup.group_name == group_name)
        .first()
    ):
        return group


def get_all_paper_groups(db: Session, offset: int = 0, limit: int = None):
    """Get all paper groups with offset and limit."""
    query = db.query(PaperGroup)
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def delete_paper_group(db: Session, group_name: str, user_id: UUID):
    """Delete paper group."""
    if paper_group := (
        db.query(PaperGroup)
        .filter(PaperGroup.group_name == group_name)
        .filter(PaperGroup.user_id == user_id)
        .first()
    ):
        if delete_paper_group_info(db, paper_group.id): # if delete paper group info success
            db.delete(paper_group)
            db.commit()
            return paper_group
        else:
            raise ValueError("Group not exist.")
            