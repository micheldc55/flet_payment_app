import json

from pydantic import BaseModel, PositiveInt


class Car(BaseModel):
    borrower_id: PositiveInt
    marca_auto: str
    modelo_auto: str

    @classmethod
    def _private_attributes(cls):
        return set(("borrower_id",))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }


class CarFactory:
    @staticmethod
    def create_from_car_record_str(car_record_str: str) -> Car:
        car_record_dict = json.loads(car_record_str)
        return Car(
            borrower_id=car_record_dict["borrower_id"],
            marca_auto=car_record_dict["marca_auto"],
            modelo_auto=car_record_dict["modelo_auto"],
        )