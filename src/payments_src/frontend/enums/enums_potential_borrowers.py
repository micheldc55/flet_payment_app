from enum import Enum


class PotentialBorrowersTitle(Enum):
    TITLE = "RDJ - Pagos"
    SUBTITLE = "Pagina de creditos potenciales"


class PagePotentialBorrowersActions(Enum):
    LIST_LOANS = "Listar Creditos (Potenciales)"
    ADD_LOAN = "Nuevo Credito (Potenciales)"
    VIEW_LOAN = "Ver Credito (Potencial)"
    EDIT_LOAN = "Editar Credito (Potencial)"

    @classmethod
    def list(cls):
        return [action.value for action in cls]
