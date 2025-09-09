import pytest

from payments_src.domain.dealerships import Dealership, DealershipFactory


def test_dealership():
    dealership = Dealership(
        dealership_id=12345678,
        name="AUTOMOTORA 23",
        dealership_code="A23-0001",
        dealership_phone_number="1234567890",
    )
    assert dealership.dealership_id == 12345678
    assert dealership.name == "AUTOMOTORA 23"
    assert dealership.dealership_code == "A23-0001"
    assert dealership.dealership_phone_number == "1234567890"


def test_factory_create_dealership():
    dealership = DealershipFactory.create_dealership(
        dealership_id=12345678,
        name="AUTOMOTORA 23",
        dealership_code="A23-0001",
        dealership_phone_number="1234567890",
    )
    assert dealership.dealership_id == 12345678
    assert dealership.name == "AUTOMOTORA 23"
    assert dealership.dealership_code == "A23-0001"
    assert dealership.dealership_phone_number == "1234567890"


def test_dealrship_raises_errors():
    with pytest.raises(ValueError):
        Dealership(
            dealership_id=-12345678,
            name="AUTOMOTORA 23",
            dealership_code="A23",
            dealership_phone_number="1234567890",
        )

    with pytest.raises(ValueError):
        Dealership(
            dealership_id=0,
            name="AUTOMOTORA 23",
            dealership_code="A23",
            dealership_phone_number="1234567890",
        )

    with pytest.raises(ValueError):
        Dealership(
            dealership_id=12345678,
            name="AUTOMOTORA 23",
            dealership_code=1234,
            dealership_phone_number="1234567890",
        )

    with pytest.raises(ValueError):
        Dealership(
            dealership_id=12345678,
            name="AUTOMOTORA 23",
            dealership_code="A23",
            dealership_phone_number=95786456,
        )
