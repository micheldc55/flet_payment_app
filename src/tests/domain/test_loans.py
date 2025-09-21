from datetime import datetime

import pytest

from payments_src.domain.borrowers import Borrower, BorrowerFactory
from payments_src.domain.car import Car
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.domain.loans import Loan, LoanFactory
from payments_src.domain.payment_enums import Currency, PaymentStatus
from payments_src.domain.payments import PaymentList, PaymentListFactory


@pytest.fixture
def borrower_charles() -> Borrower:
    return BorrowerFactory.create_borrower(
        borrower_id=12345678,
        name="Charles",
        phone_number="1234567890",
        notes="No notes",
        path_to_files="path/to/files",
    )


@pytest.fixture
def dealership_automotora_carlos_gonzalez() -> Dealership:
    return DealershipFactory.create_dealership(
        dealership_id=12345678,
        name="AUTOMOTORA CARLOS GONZALEZ",
        dealership_code="ACG",
        dealership_phone_number="1234567890",
    )


@pytest.fixture
def payment_list_charles() -> PaymentList:
    return PaymentListFactory.create_payment_list(
        dinero_total_prestado=10000,
        tasa_interes=0.02,
        pago_mensual=1000,
        fecha_inicio=datetime(2025, 7, 1),
        num_pagos=12,
        moneda=Currency.UYU,
        ids=None,
    )


@pytest.fixture
def car_toyota() -> Car:
    return Car(
        borrower_id=12345678,
        marca_auto="Toyota",
        modelo_auto="Corolla",
    )


def test_loan(borrower_charles, dealership_automotora_carlos_gonzalez, payment_list_charles, car_toyota):
    loan = Loan(
        loan_id=12345678,
        loan_readable_code="ACG-0001",
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        car=car_toyota,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    assert loan.loan_id == 12345678
    assert loan.loan_readable_code == "ACG-0001"
    assert loan.payment_list == payment_list_charles
    assert loan.borrower == borrower_charles
    assert loan.car == car_toyota
    assert loan.dealership == dealership_automotora_carlos_gonzalez


def test_loan_factory_create_loan(
    payment_list_charles, borrower_charles, dealership_automotora_carlos_gonzalez, car_toyota
):
    loan = LoanFactory.create_loan(
        loan_id=12345678,
        loan_number=100,
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        car=car_toyota,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    assert loan.loan_id == 12345678
    assert loan.loan_readable_code == "ACG-00000100"


def test_loan_json_serialization_deserialization(
    borrower_charles, dealership_automotora_carlos_gonzalez, payment_list_charles, car_toyota
):
    """Test that Loan objects can be serialized to JSON and deserialized back correctly."""
    original_loan = Loan(
        loan_id=12345678,
        loan_readable_code="ACG-0001",
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        car=car_toyota,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    json_dict = original_loan.to_json_dict()

    assert isinstance(json_dict["payment_list"], str)
    assert isinstance(json_dict["borrower"], str)
    assert isinstance(json_dict["car"], str)
    assert isinstance(json_dict["dealership"], str)
    assert json_dict["loan_id"] == 12345678
    assert json_dict["loan_readable_code"] == "ACG-0001"

    deserialized_loan = Loan.from_json_dict(json_dict)

    assert deserialized_loan.loan_id == original_loan.loan_id
    assert deserialized_loan.loan_readable_code == original_loan.loan_readable_code
    assert deserialized_loan.payment_list.model_dump() == original_loan.payment_list.model_dump()
    assert deserialized_loan.borrower.model_dump() == original_loan.borrower.model_dump()
    assert deserialized_loan.car.model_dump() == original_loan.car.model_dump()
    assert deserialized_loan.dealership.model_dump() == original_loan.dealership.model_dump()


def test_loan_factory_create_loan_from_csv_row(
    borrower_charles, dealership_automotora_carlos_gonzalez, payment_list_charles, car_toyota
):
    """Test that LoanFactory can create loans from CSV row data."""
    original_loan = Loan(
        loan_id=12345678,
        loan_readable_code="ACG-0001",
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        car=car_toyota,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    csv_row = original_loan.to_json_dict()

    loan_from_csv = LoanFactory.create_loan_from_csv_row(csv_row)

    assert loan_from_csv.loan_id == original_loan.loan_id
    assert loan_from_csv.loan_readable_code == original_loan.loan_readable_code
    assert loan_from_csv.payment_list.model_dump() == original_loan.payment_list.model_dump()
    assert loan_from_csv.borrower.model_dump() == original_loan.borrower.model_dump()
    assert loan_from_csv.car.model_dump() == original_loan.car.model_dump()
    assert loan_from_csv.dealership.model_dump() == original_loan.dealership.model_dump()
