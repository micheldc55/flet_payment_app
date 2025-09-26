from enum import Enum


class ActiveLoansActions(Enum):
    LIST_LOANS = "Listar Préstamos Activos"
    VIEW_LOAN = "Ver Préstamo"
    VIEW_LOAN_PAYMENTS = "Ver Pagos"
    VIEW_MONTHLY_PAYMENTS = "Ver Pagos por Mes"

    @classmethod
    def list(cls):
        return [action.value for action in cls]
