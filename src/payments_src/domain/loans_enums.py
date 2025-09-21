from enum import Enum


class LoanConstants(Enum):
    LOAN_ID_TOTAL_DIGITS = 8


class LoanStatus(Enum):
    POTENTIAL = "Pendiente de Aprobación"
    REJECTED = "Rechazado"
    APPROVED = "Aprobado"
