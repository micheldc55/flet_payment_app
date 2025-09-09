from pydantic import BaseModel, ConfigDict, PositiveInt


class Dealership(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    dealership_id: PositiveInt
    name: str
    dealership_code: str
    dealership_phone_number: str


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
