import pytest
from pydantic import ValidationError

from payments_src.domain.car import Car


@pytest.fixture
def toyota_corolla() -> Car:
    return Car(
        borrower_id=1,
        marca_auto="Toyota",
        modelo_auto="Corolla",
    )


def test_car(toyota_corolla: Car):
    assert toyota_corolla.borrower_id == 1
    assert toyota_corolla.marca_auto == "Toyota"
    assert toyota_corolla.modelo_auto == "Corolla"


def test_car_get_fields_and_types():
    parsed_fields = Car.get_fields_and_types()
    parsed_fields = {
        field: field_info.annotation
        for field, field_info in Car.model_fields.items()
        if field not in Car._private_attributes()
    }

    assert parsed_fields == {
        "marca_auto": str,
        "modelo_auto": str,
    }


def test_car_raises_type_errors():
    with pytest.raises(ValidationError):
        Car(
            borrower_id=1,
            marca_auto=1,
            modelo_auto="Corolla",
        )

    with pytest.raises(ValidationError):
        Car(
            borrower_id=1,
            marca_auto="Toyota",
            modelo_auto=1,
        )
