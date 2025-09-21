import os
from datetime import datetime

from pydantic import BaseModel, PositiveInt


class FileObject(BaseModel):
    file_name: str
    file_readable_name: str
    file_type: str
    file_path: str
    added_date: datetime
    file_group_id: PositiveInt
    file_id: PositiveInt


class FileGroup(BaseModel):
    file_group_id: PositiveInt
    file_group_name: str
    borrower_id: PositiveInt
    files: dict[PositiveInt, FileObject]

    def add_file(self, file: FileObject) -> None:
        self.files[file.file_id] = file

    def remove_file(self, file_id: PositiveInt) -> None:
        del self.files[file_id]

    def retrieve_file_by_id(self, file_id: PositiveInt) -> FileObject:
        return self.files[file_id]
