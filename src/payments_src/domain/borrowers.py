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

    def _private_attributes(self):
        return set(("borrower_id", "path_to_files"))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: type(getattr(cls, field)) for field in cls.model_fields if field not in cls._private_attributes()
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
