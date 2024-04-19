"""Paper group services."""
# pylint: disable=E0401
from __future__ import annotations

from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
import pandas as pd

from db.models import SessionLocal, PaperGroup
import db.execute.user as user_execute
import db.execute.paper_group as paper_group_execute

from logger.logger import custom_logger


class PaperGroupService:
    """Paper group service."""

    def __init__(self):
        self.db = SessionLocal()
        self.group_columns = ["Group ID", "Group name", "User ID"]

    def create_paper_group(self, data: dict) -> dict | None:
        """Create paper group."""
        try:
            paper_group = PaperGroup(
                group_name=data['group_name'],
                user_id=data['user_id'],
            )
            if user := user_execute.get_user_by_id(self.db, paper_group.user_id):
                if paper_group_execute.get_group_by_group_name(self.db, paper_group.group_name):
                    raise ValueError(f"Group '{paper_group.group_name}' existed.")
                if paper_group_execute.create_paper_group(self.db, paper_group):
                    return "Create new paper group succesfully."
            else:
                raise ValueError(f"User '{user.username}' existed.")
            
        except ValueError as e:
            custom_logger.error(str(e))
        
        except Exception as e:
            custom_logger.error(str(e))
        return str(e)

    def get_groups_by_user_id(self, user_id: UUID) -> List[PaperGroup]:
        """Get paper groups by user id."""
        return paper_group_execute.get_groups_by_user_id(self.db, user_id)

    def get_group_by_id(self, group_id: UUID) -> PaperGroup:
        """Get paper group by user group_id."""
        return paper_group_execute.get_group_by_id(self.db, group_id)

    def get_group_by_group_name(self, group_name: str) -> PaperGroup:
        """Get paper group by user group_name."""
        return paper_group_execute.get_group_by_group_name(self.db, group_name)

    def get_groups_by_name_user_id(self, group_name: str, user_id: UUID) -> PaperGroup:
        """Get paper group by user group name, user_id."""
        return paper_group_execute.get_groups_by_name_user_id(self.db, group_name, user_id)

    def get_all_paper_groups(self, offset: int = 0, limit: int = 100000000) -> List[PaperGroup]:
        """Get all paper groups."""
        return paper_group_execute.get_all_paper_groups(self.db, offset, limit)

    def delete_paper_group(self, group_name: str, user_id: UUID) -> PaperGroup | None:
        """Delete a paper group."""
        try:
            if paper_group_execute.delete_paper_group(self.db, group_name, user_id):
                return "Delete group successfully."
        
        except ValueError as e:
            custom_logger.error(str(e))
            return str(e)
