from enum import Enum


class SidebarTitle(Enum):
    TITLE = "RDJ - Pagos"


class SidebarOptions(Enum):
    INICIO = "Inicio"
    CALCULADORA_DE_PAGOS = "Calculadora de Pagos"
    CREDITOS_POTENCIALES = "Creditos Potenciales"
    CREDITOS_ACTIVOS = "Creditos Activos"
    ESTADISTICAS = "Estadisticas"
    GESTION_AUTOMOTORAS = "Gestion de Automotoras"

    @classmethod
    def list(cls):
        return [option.value for option in cls]


