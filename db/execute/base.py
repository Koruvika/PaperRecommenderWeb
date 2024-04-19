"""Base Execute."""
# pylint: disable=E0401
from __future__ import annotations
from db.models import CustomBaseModel


class BaseExecute:
    """Base Execute."""

    def __init__(self, data_collection, convert_helper):
        self.data_collection = data_collection
        self.convert_helper = convert_helper

    def retrieve_datas(self, offset: int = 0, limit: int = None) -> list[CustomBaseModel]:
        """Retrieve all data."""
        datas = []
        for data in self.data_collection.find().skip(offset).limit(limit):
            datas.append(self.convert_helper(data))
        return datas

    def add_data(self, data: CustomBaseModel) -> CustomBaseModel:
        """Add a new data."""
        data = self.data_collection.insert_one(data)
        new_data = self.data_collection.find_one({"_id": data.inserted_id})
        return self.convert_helper(new_data)

    def retrieve_data_by_id(self, id: str) -> CustomBaseModel | None:
        """Retrieve a data with a matching ID."""
        data = self.data_collection.find_one({"_id": id})
        if data:
            return self.convert_helper(data)
        return None

    def update_data(self, id: str, update_data: dict) -> bool:
        """Update a data with a matching ID."""
        data = self.data_collection.find_one({"_id": id})
        if data:
            updated_data = self.data_collection.update_one({"_id": id},
                                                           {"$set": update_data})
            return bool(updated_data)
        return False

    def delete_data(self, id: str) -> bool:
        """Delete data by ID."""
        data = self.data_collection.find_one({"_id": id})
        if data:
            self.data_collection.delete_one({"_id": id})
            return True
        return False
