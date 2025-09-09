from enum import Enum


class PotentialBorrowerStatus(Enum):
    POTENTIAL = "Pendiente de Aprobación"
    REJECTED = "Rechazado"
    APPROVED = "Aprobado"
