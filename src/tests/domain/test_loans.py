from datetime import datetime

import pytest

from payments_src.domain.borrowers import Borrower, BorrowerFactory
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


def test_loan(borrower_charles, dealership_automotora_carlos_gonzalez, payment_list_charles):
    loan = Loan(
        loan_id=12345678,
        loan_readable_code="ACG-0001",
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    assert loan.loan_id == 12345678
    assert loan.loan_readable_code == "ACG-0001"
    assert loan.payment_list == payment_list_charles
    assert loan.borrower == borrower_charles
    assert loan.dealership == dealership_automotora_carlos_gonzalez


def test_loan_factory_create_loan(
        payment_list_charles,
        borrower_charles,
        dealership_automotora_carlos_gonzalez
    ):
    loan = LoanFactory.create_loan(
        loan_id=12345678,
        loan_number=100,
        payment_list=payment_list_charles,
        borrower=borrower_charles,
        dealership=dealership_automotora_carlos_gonzalez,
    )

    assert loan.loan_id == 12345678
    assert loan.loan_readable_code == "ACG-00000100"