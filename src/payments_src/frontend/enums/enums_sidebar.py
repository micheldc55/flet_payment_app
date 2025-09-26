from enum import Enum


class SidebarTitle(Enum):
    TITLE = "RDJ - Pagos"


class SidebarOptions(Enum):
    INICIO = "Inicio"
    CALCULADORA_DE_PAGOS = "Calculadora de Pagos"
    CREDITOS_POTENCIALES = "Creditos Potenciales"
    CREDITOS_ACTIVOS = "Creditos Activos"
    PAYMENT_MANAGEMENT = "Gestion de Pagos"
    ESTADISTICAS = "Estadisticas"
    GESTION_AUTOMOTORAS = "Gestion de Automotoras"

    @classmethod
    def list(cls):
        return [option.value for option in cls]


class SidebarQuickAccess(Enum):
    CALCULADORA_DE_PAGOS = "Calculadora de Pagos"
    OCULTAR = "Ocultar"

    @classmethod
    def list(cls):
        return [option.value for option in cls]