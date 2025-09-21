from pydantic import BaseModel, ConfigDict, PositiveInt


class Dealership(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    dealership_id: PositiveInt
    name: str
    dealership_code: str
    dealership_phone_number: str

    @classmethod
    def _private_attributes(cls):
        return set(("dealership_id", ))
    
    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }



class DealershipFactory:
    def create_dealership(
        dealership_id: PositiveInt,
        name: str,
        dealership_code: str,
        dealership_phone_number: str,
    ) -> Dealership:
        return Dealership(
            dealership_id=dealership_id,
            name=name,
            dealership_code=dealership_code,
            dealership_phone_number=dealership_phone_number,
        )