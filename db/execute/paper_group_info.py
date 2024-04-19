"""Paper group info execute."""
# pylint: disable=E0401
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session
from db.models import PaperGroupInformation


def create_group_info(db: Session, group_info: PaperGroupInformation) -> PaperGroupInformation:
    """Create PaperGroupInformation."""
    db.add(group_info)
    db.commit()
    db.refresh(group_info)
    return group_info


def check_paper_exist_in_group(db: Session, group_id: UUID, paper_id: str) -> PaperGroupInformation:
    """Check paper exist in group."""
    if group_info := (
        db.query(PaperGroupInformation)
        .filter(PaperGroupInformation.id == group_id)
        .filter(PaperGroupInformation.paper_id == paper_id)
        .first()
    ):
        return group_info


def get_papers_by_group_id(db: Session, group_id: UUID):
    """Get paper by group_id."""
    paper_group_infos = []
    if group_infos := (
        db.query(PaperGroupInformation)
        .filter(PaperGroupInformation.id == group_id)
        .all()
    ):
        for group_info in group_infos:
            paper_group_infos.append([
                group_info.group_id,
                group_info.paper_id,
                group_info.date,
                group_info.appropriate,
            ])
        return paper_group_infos


def update_appropriate(
    db: Session,
    group_id: UUID,
    paper_id: str,
    appropriate: bool
) -> PaperGroupInformation:
    """Update appropriate."""
    if group_info := check_paper_exist_in_group(db, group_id, paper_id):
        group_info.appropriate = appropriate
        db.commit()
        db.refresh(group_info)
        return group_info
    else:
        raise ValueError("Group not exist.")


def delete_paper_in_group(db: Session, group_id: UUID, paper_id: str):
    """Delete paper in group."""
    if paper_of_group := (
        db.query(PaperGroupInformation)
        .filter(PaperGroupInformation.id == group_id)
        .filter(PaperGroupInformation.paper_id == paper_id)
        .first()
    ):
        db.delete(paper_of_group)
        db.commit()
        return paper_of_group
    else:
        raise ValueError(f"Paper {paper_id} not exist in group {group_id}.")


def delete_paper_group_info(db: Session, group_id: UUID) -> bool:
    """Delete paper group information."""
    if paper_in_group := (
        db.query(PaperGroupInformation)
        .filter(PaperGroupInformation.id == group_id)
        .all()
    ):
        for paper in paper_in_group:
            db.delete(paper)
            db.commit()
        return True
    else:
        return None
