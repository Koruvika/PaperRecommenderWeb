"""Paper group services."""
# pylint: disable=E0401
from __future__ import annotations

from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
import pandas as pd

from db.models import SessionLocal, PaperGroupInformation
import db.execute.user as user_execute
import db.execute.paper as paper_execute
import db.execute.paper_group as paper_group_execute
import db.execute.paper_group_info as paper_group_info_execute

from logger.logger import custom_logger


class PaperGroupInfoService:
    """Paper group information service."""

    def __init__(self):
        self.db = SessionLocal()
        self.group_info_columns = ["Group ID", "Paper ID", "Date", "Appropriate"]

    def insert_paper_to_group(self, data: dict) -> dict:
        """Create paper group information."""
        try:
            paper_group_info = PaperGroupInformation(
                id=data['group_id'],
                paper_id=data['paper_id'],
                appropriate=data['appropriate'],
            )
            if paper_execute.check_paper_exist(self.db, paper_group_info.paper_id):
                if group_info := paper_group_execute.get_group_by_id(self.db, paper_group_info.id):
                    if paper_group_info_execute.check_paper_exist_in_group(
                        self.db,
                        paper_group_info.id,
                        paper_group_info.paper_id,
                    ):
                        raise ValueError(f"Paper has existed in group '{group_info.group_name}'.")
                    if paper_group_info_execute.create_group_info(self.db, paper_group_info):
                        return "Paper successfully inserted into group."
                else:
                    raise ValueError(f"Group {paper_group_info.id} not existed.")
            else:
                raise ValueError(f"Paper {paper_group_info.paper_id} not existed.")
        
        except ValueError as e:
            custom_logger.error(str(e))
        
        except Exception as e:
            custom_logger.error(str(e))
        return str(e)

    def get_papers_by_group_id(self, group_id: UUID):
        """Get papers by group_id."""
        results = paper_group_info_execute.get_papers_by_group_id(self.db, group_id)
        return pd.DataFrame(results, columns=self.group_info_columns)

    def update_appropriate(
        self,
        group_id: UUID,
        paper_id: str,
        appropriate: bool,
    ):
        """Update paper appropriate."""
        try:
            if paper_group_info_execute.update_appropriate(
                self.db,
                group_id,
                paper_id,
                appropriate
            ):
                return "Update group information successfully."

        except ValueError as e:
            custom_logger.error(str(e))
            return str(e)

    def delete_paper_of_group(self, group_id: UUID,  paper_id: str):
        """Delete paper of group."""
        try:
            if paper_group_info_execute.delete_paper_in_group(self.db, group_id, paper_id):
                return "Delete group information successfully."
        
        except ValueError as e:
            custom_logger.error(str(e))
            return str(e)
