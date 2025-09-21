from enum import Enum


class DealershipManagementActions(Enum):
    ADD_DEALERSHIP = "Agregar Automotora"
    VIEW_DEALERSHIP = "Ver Automotora"
    EDIT_DEALERSHIP = "Editar Automotora"
    DELETE_DEALERSHIP = "Eliminar Automotora"

    @classmethod
    def list(cls):
        return [action.value for action in cls]