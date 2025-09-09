from enum import Enum


class PaymentStatus(Enum):
    PENDING = "pendiente"
    PAID = "pago"
    CANCELLED = "cancelado"


class Currency(Enum):
    USD = "USD"
    UYU = "UYU"
    EUR = "EUR"

    @classmethod
    def list(cls):
        return [currency.value for currency in cls]
