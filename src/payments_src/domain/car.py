from pydantic import BaseModel, PositiveInt


class Car(BaseModel):
    borrower_id: PositiveInt
    marca_auto: str
    modelo_auto: str

    @classmethod
    def _private_attributes(cls):
        return set(("borrower_id",  ))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }
    