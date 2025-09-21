import pandas as pd
from pydantic import ConfigDict

from payments_src.domain.borrower_enums import PotentialBorrowerStatus
from payments_src.domain.borrowers import Borrower


class PotentialBorrower(Borrower):
    model_config = ConfigDict(use_enum_values=True)
    status: PotentialBorrowerStatus

    def approve_loan(self):
        self.status = PotentialBorrowerStatus.APPROVED.value

    def reject_loan(self):
        self.status = PotentialBorrowerStatus.REJECTED.value

    def get_status(self):
        return self.status

    @classmethod
    def _private_attributes(cls):
        return set(("borrower_id", "path_to_files", "status"))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }

    @classmethod
    def _non_displayable_attributes(cls):
        return ["path_to_files"]

    def create_borrower_from_potential_borrower(self) -> Borrower:
        return Borrower(
            borrower_id=self.borrower_id,
            nombre_cliente=self.nombre_cliente,
            telefono_cliente=self.telefono_cliente,
            notas=self.notas,
            path_to_files=self.path_to_files,
        )
