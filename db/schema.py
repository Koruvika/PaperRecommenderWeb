"""File Infor Schema."""

from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class PaperInformationCreateSchema(BaseModel):
    """Schema for paper information upload."""

    id: str = Field(..., description="Unique identifier of file.")
    title: str = Field(..., description="Title of paper.")
    link: Optional[str] = Field(..., description="Content of file.")
    publish_year: Optional[int] = Field(..., description="Publish year of paper.")
    abstract: Optional[str] = Field(..., description="Abstract of paper.")
    n_citations: Optional[int] = Field(..., description="Number citations of paper.")
    author: Optional[List[str]] = Field(..., description="Authors of paper.")
    conference: Optional[str] = Field(..., description="Publish conference of paper.")
    tag: Optional[List[str]] = Field(..., description="Tags of paper.")

    class Config:
        from_attributes = True


class PaperInformationUpdateSchema(BaseModel):
    """Schema for paper information update."""

    id: str = Field(..., description="Unique identifier of file.")
    link: Optional[str] = Field(..., description="Content of file.")
    n_citations: Optional[int] = Field(..., description="Number citations of paper.")
    conference: Optional[str] = Field(..., description="Publish conference of paper.")

    class Config:
        from_attributes = True
