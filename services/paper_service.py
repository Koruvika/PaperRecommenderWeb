"""Paper services."""
# pylint: disable=E0401
from __future__ import annotations

from sqlalchemy.orm import Session
import pandas as pd

from db.models import SessionLocal, PaperInformation
from db.schema import PaperInformationUpdateSchema
import db.execute.paper as paper_execute

from logger.logger import custom_logger


class PaperService:
    """Paper service."""

    def __init__(self):
        self.db = SessionLocal()
        self.paper_columns = ["Paper ID", "Name", "Year", "Abstract"]

    def create_paper(self, paper_info: dict):
        """Create paper."""
        try:
            paper_info_create = PaperInformation(
                id=paper_info['id'],
                title=paper_info['title'],
                link=paper_info['link'],
                publish_year=paper_info['publish_year'],
                abstract = paper_info['abstract'],
                n_citations=paper_info['n_citations'],
                author=paper_info['author'],
                conference=paper_info['conference'],
                # conference_link=paper_info['conference_link'],
                tag=paper_info['tag'],
            )
            if paper_execute.check_paper_exist(self.db, paper_info['id']):
                raise ValueError(f"Paper '{paper_info['title']}' existed.")
            return paper_execute.create_paper_info(self.db, paper_info_create)
        
        except ValueError as e:
            custom_logger.error(str(e))

        except Exception as e:
            custom_logger.error(str(e))
        return None

    def update_paper_info(
        self,
        paper_id: str,
        paper_link: str,
        paper_citation: int,
        paper_conference: str,
    ):
        """Update paper information."""
        if paper_execute.check_paper_exist(self.db, paper_id):
            try:
                update_info = PaperInformationUpdateSchema(
                    id=paper_id,
                    link=paper_link,
                    n_citations=paper_citation,
                    conference=paper_conference,
                )
                paper_execute.update_paper_info(self.db, update_info)
            
            except ValueError as e:
                custom_logger.error(str(e))
                
            except Exception as e:
                custom_logger.error(str(e))
            return str(e)
        else:
            msg = f"Paper id {paper_id} not existed."
            custom_logger.error(msg)
            return msg

    def get_all_papers(self, offset: int = 0, limit: int = None):
        """Get all papers."""
        return paper_execute.get_all_papers(self.db, offset, limit)

    def get_paper(self, paper_name: str):
        """Get paper by paper name."""
        return paper_execute.get_paper_by_paper_name(self.db, paper_name)

    def get_papers_by_text(self, text_search: str):
        """Get paper by text."""
        results = paper_execute.get_papers_by_text(self.db, text_search)
        return pd.DataFrame(results, columns=self.paper_columns)

    def get_paper_by_paper_id(self, paper_id: str):
        """Get paper by paper_id."""
        res = paper_execute.get_paper_by_paper_id(self.db, paper_id)
        return {
            "Paper ID": res.id,
            "Name": res.title,
            "Year": res.publish_year,
            "Abstract": res.abstract,
        }

    def get_papers_by_list_paper_ids(self, paper_ids: List[str]):
        """Get paper by list of paper_id."""
        results = paper_execute.get_paper_by_list_paper_ids(self.db, group_id)
        return pd.DataFrame(results, columns=self.paper_columns)

    def delete_paper(self, paper_title: str):
        """Delete paper by title."""
        try:
            if paper_execute.delete_paper(self.db, paper_title):
                return f"Delete paper {paper_title} succesfully."
        
        except ValueError as e:
            custom_logger.error(str(e))

        except Exception as e:
            custom_logger.error(str(e))
        return str(e)
