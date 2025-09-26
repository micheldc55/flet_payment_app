from datetime import datetime

import pydantic
import pytest

from payments_src.domain.payment_enums import Currency, PaymentStatus
from payments_src.domain.payments import Payment, PaymentFactory, PaymentList, PaymentListFactory


def test_payment():
    payment = Payment(
        amount=100,
        end_date=datetime(2025, 1, 1),
        id=12345678,
        status=PaymentStatus.PENDING.value,
    )
    assert payment.amount == 100
    assert payment.end_date == datetime(2025, 1, 1)
    assert payment.status == PaymentStatus.PENDING.value
    assert payment.id == 12345678


def test_payment_raises_validation_error():
    with pytest.raises(pydantic.ValidationError):
        Payment(
            amount=-100,
            end_date=datetime(2025, 1, 1),
            id=12345678,
            status=PaymentStatus.PAID,
        )

    with pytest.raises(pydantic.ValidationError):
        Payment(amount=100, end_date="2025-01-01", id=-12345678, status=PaymentStatus.PAID)

    with pytest.raises(pydantic.ValidationError):
        Payment(amount=100, end_date=datetime(2025, 1, 1), id=0, status=PaymentStatus.PAID)

    with pytest.raises(pydantic.ValidationError):
        Payment(
            amount=100,
            end_date=datetime(2025, 1, 1),
            id=-12345678,
            status=PaymentStatus.PAID,
        )

    with pytest.raises(pydantic.ValidationError):
        Payment(
            amount=100,
            end_date=datetime(2025, 1, 1),
            id=12345678,
            status="STATUS FALSO",
        )


def test_factory_create_payment():
    payment = PaymentFactory.create_payment(amount=100, end_date=datetime(2025, 1, 1), id=12345678)
    assert payment.amount == 100
    assert payment.end_date == datetime(2025, 1, 1)
    assert payment.status == PaymentStatus.PENDING.value
    assert payment.id == 12345678


def test_payment_list():
    payment_list = PaymentList(
        payments={
            12345678: Payment(
                amount=100,
                end_date=datetime(2025, 1, 1),
                id=12345678,
                status=PaymentStatus.PENDING.value,
            ),
        },
        num_pagos=1,
        fecha_inicio=datetime(2025, 1, 1),
        dinero_total_prestado=1000,
        tasa_interes=0.05,
        pago_mensual=100,
        moneda=Currency.UYU,
    )

    assert payment_list.payments[12345678].amount == 100
    assert payment_list.payments[12345678].end_date == datetime(2025, 1, 1)
    assert payment_list.payments[12345678].status == PaymentStatus.PENDING.value
    assert payment_list.payments[12345678].id == 12345678
    assert payment_list.num_pagos == 1
    assert payment_list.fecha_inicio == datetime(2025, 1, 1)
    assert payment_list.dinero_total_prestado == 1000
    assert payment_list.tasa_interes == 0.05
    assert payment_list.pago_mensual == 100
    assert payment_list.moneda == Currency.UYU


def test_factory_create_payment_list():
    payment_list = PaymentListFactory.create_payment_list(
        dinero_total_prestado=1000,
        tasa_interes=0.05,
        pago_mensual=100,
        fecha_inicio=datetime(2025, 1, 1),
        num_pagos=12,
        moneda=Currency.USD,
        ids=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    )
    assert len(payment_list.payments) == 12
    assert payment_list.payments[10].amount == 100
    assert payment_list.payments[10].end_date == datetime(2025, 1, 1)
    assert payment_list.payments[10].status == PaymentStatus.PENDING.value
    assert payment_list.payments[10].id == 10
    assert payment_list.payments[20].id == 20
    assert payment_list.payments[120].id == 120
    assert payment_list.dinero_total_prestado == 1000
    assert payment_list.tasa_interes == 0.05
    assert payment_list.pago_mensual == 100
    assert payment_list.fecha_inicio == datetime(2025, 1, 1)
    assert payment_list.num_pagos == 12
    assert payment_list.moneda == Currency.USD


def test_factory_create_payment_list_no_ids():
    payment_list = PaymentListFactory.create_payment_list(
        dinero_total_prestado=1000,
        tasa_interes=0.05,
        pago_mensual=100,
        fecha_inicio=datetime(2025, 1, 1),
        num_pagos=12,
        moneda=Currency.UYU,
        ids=None,
    )

    assert payment_list.payments[1].id == 1
    assert payment_list.payments[2].id == 2
    assert payment_list.payments[12].id == 12


def test_payment_list_raises_validation_error():
    with pytest.raises(pydantic.ValidationError):
        PaymentList(
            tasa_interes=-0.05,
            pago_mensual=100,
            fecha_inicio=datetime(2025, 1, 1),
            num_pagos=12,
            moneda=Currency.UYU,
            payments={
                1: Payment(
                    amount=100,
                    end_date=datetime(2025, 1, 1),
                    id=1,
                    status=PaymentStatus.PENDING,
                ),
            },
        )

    with pytest.raises(pydantic.ValidationError):
        PaymentList(
            tasa_interes=1.05,
            pago_mensual=100,
            fecha_inicio=datetime(2025, 1, 1),
            num_pagos=12,
            moneda=Currency.UYU,
            payments={
                1: Payment(
                    amount=100,
                    end_date=datetime(2025, 1, 1),
                    id=1,
                    status=PaymentStatus.PENDING,
                ),
            },
        )