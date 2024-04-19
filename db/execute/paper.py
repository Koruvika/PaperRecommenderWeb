"""Paper execute."""
# pylint: disable=E0401
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID
from typing import List

from sqlalchemy.orm import Session
from db.models import PaperInformation
from db.schema import PaperInformationUpdateSchema


def create_paper_info(db: Session, paper_info: PaperInformation) -> PaperInformation:
    """Create paper info. """
    db.add(paper_info)
    db.commit()
    db.refresh(paper_info)
    return paper_info


def check_paper_exist(db: Session, paper_id: str) -> PaperInformation:
    """Check paper existed."""
    return (
        db.query(PaperInformation)
        .filter(PaperInformation.id == paper_id).first()
    )


def get_all_papers(db: Session, offset: int = 0, limit: int = None):
    """Get all papers with offset and limit."""
    query = db.query(PaperInformation).order_by(PaperInformation.publish_year.desc())
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def get_paper_by_paper_id(db: Session, paper_id: str) -> PaperInformation:
    """Get paper with paper id."""
    if paper := db.query(PaperInformation).filter(PaperInformation.id == paper_id).first():
        return paper


def get_paper_by_list_paper_ids(db: Session, paper_ids: List[str]) -> PaperInformation:
    """Get paper with list paper id."""
    papers = []
    for paper_id in paper_ids:
        if paper := db.query(PaperInformation).filter(PaperInformation.id == paper_id).first():
            papers.append([paper.id, paper.title, paper.publish_year. paper.abstract])

    return papers


def get_paper_by_paper_name(db: Session, paper_name: str) -> PaperInformation:
    """Get paper with paper name."""
    if paper := db.query(PaperInformation).filter(PaperInformation.title == paper_name).first():
        return paper


def get_papers_by_text(db: Session, text_search: str):
    """Get paper by text search."""
    results = []
    if papers := (
        db.query(PaperInformation)
        .filter(PaperInformation.title.ilike(f'%{text_search}%'))
        .all()
    ):
        for paper in papers:
            results.append([paper.id, paper.title, paper.publish_year. paper.abstract])
        return results
        

def update_paper_info(db: Session, update_info: PaperInformationUpdateSchema) -> PaperInformation:
    """Update paper info."""
    if change_paper := (
        db.query(PaperInformation)
        .filter(PaperInformation.id == update_info.id)
        .first()
    ):
        change_paper.link = update_info.link
        change_paper.n_citations = update_info.n_citations
        change_paper.conference = update_info.conference
        db.commit()
        db.refresh(change_paper)
        return change_paper
    else:
        raise ValueError("Paper not found.")


def delete_paper(db: Session, paper_title: str) -> PaperInformation:
    """Delete paper."""
    if paper := (
        db.query(PaperInformation)
        .filter(PaperInformation.title == paper_title)
        .first()
    ):
        db.delete(paper)
        db.commit()
        return paper
    else:
        raise ValueError("Paper not found.")
