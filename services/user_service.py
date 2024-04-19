"""User services."""
# pylint: disable=E0401
from __future__ import annotations

from sqlalchemy.orm import Session
import pandas as pd

from db.models import SessionLocal, User
import db.execute.user as user_execute

from logger.logger import custom_logger


class UserService:
    """User services."""

    def __init__(self):
        self.db = SessionLocal()
        self.user_columns = ["ID", "User ID", "Username", "Password", "Name", "Email"]

    def create_user(self, data: dict) -> dict:
        """Create a new user."""
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                hashed_password=data['password'],
                name=data['name'],
            )
            if user_execute.check_user_exist(self.db, user.username):
                raise ValueError(f"User '{user.username}' existed.")
            if new_user := user_execute.create_user(self.db, user_execute):
                return "Insert new user successfully.", new_user.id
        
        except ValueError as e:
            custom_logger.error(str(e))
            return e

        except Exception as e:
            custom_logger.error(str(e))
            return str(e)
