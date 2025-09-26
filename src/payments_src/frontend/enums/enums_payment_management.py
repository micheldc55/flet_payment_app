from enum import Enum


class PaymentManagementActions(Enum):
    MARK_AS_PAID = "Marcar como Pagado"
    EDIT_PAYMENT = "Editar Pago"
    VIEW_PAYMENTS = "Ver Pagos"

    @classmethod
    def list(cls):
        return [action.value for action in cls]


class PaymentFilterType(Enum):
    BY_BORROWER = "Por Cliente"
    BY_MONTH = "Por Mes"

    @classmethod
    def list(cls):
        return [filter_type.value for filter_type in cls]
