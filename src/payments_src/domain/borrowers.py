import json
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, PositiveInt


class Borrower(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    borrower_id: PositiveInt
    nombre_cliente: str
    telefono_cliente: str
    notas: str
    path_to_files: Optional[str] = None

    @classmethod
    def _private_attributes(cls):
        return set(("borrower_id", "path_to_files"))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }

    @classmethod
    def get_displayable_columns(cls):
        return [field for field, _ in cls.model_fields.items() if field not in cls._non_displayable_attributes()]

    def to_printable_dataframe(self):
        columns = self.get_displayable_columns()
        values = [
            str(getattr(self, field)) if getattr(self, field) is not None else "N/A"  # --> handle None values
            for field in columns
        ]
        return pd.DataFrame({"propiedad": columns, "valor": values})


class BorrowerFactory:
    @staticmethod
    def create_borrower(
        borrower_id: PositiveInt,
        name: str,
        phone_number: str,
        notes: str,
        path_to_files: Optional[str] = None,
    ) -> Borrower:
        return Borrower(
            borrower_id=borrower_id,
            nombre_cliente=name,
            telefono_cliente=phone_number,
            notas=notes,
            path_to_files=path_to_files,
        )

    
    @staticmethod
    def create_from_borrower_record_str(borrower_record_str: str) -> Borrower:
        borrower_record_dict = json.loads(borrower_record_str)
        return Borrower(
            borrower_id=borrower_record_dict["borrower_id"],
            nombre_cliente=borrower_record_dict["nombre_cliente"],
            telefono_cliente=borrower_record_dict["telefono_cliente"],
            notas=borrower_record_dict["notas"],
            path_to_files=borrower_record_dict["path_to_files"],
        )
