import json
from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, NonNegativeFloat, PositiveInt, PositiveFloat

from payments_src.domain.payment_enums import Currency, PaymentStatus


class Payment(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    id: PositiveInt
    amount: NonNegativeFloat
    end_date: datetime
    status: PaymentStatus

    def change_status(self, status: PaymentStatus) -> None:
        self.status = status

    def change_amount(self, amount: NonNegativeFloat) -> None:
        self.amount = amount

    def change_end_date(self, end_date: datetime) -> None:
        self.end_date = end_date


class PaymentList(BaseModel):
    fecha_inicio: datetime
    pago_mensual: PositiveFloat
    num_pagos: PositiveInt
    dinero_total_prestado: PositiveFloat
    tasa_interes: PositiveFloat
    moneda: Currency
    payments: dict[PositiveInt, Payment]

    @classmethod
    def model_validate(cls, value):
        obj = super().model_validate(value)
        if not (0 < obj.tasa_interes < 1):
            raise ValueError("tasa_interes must be a float between 0 and 1 (exclusive)")
        return obj

    def add_payment(self, payment: Payment) -> None:
        assert isinstance(payment, Payment), "You must pass a Payment object to the `add_payment` method"
        self.payments[payment.id] = payment

    def remove_payment(self, payment: Payment) -> None:
        del self.payments[payment.id]

    def retrieve_payment_by_id(self, payment_id: PositiveInt) -> Payment:
        return self.payments[payment_id]

    def calculate_total_amount(self) -> NonNegativeFloat:
        return sum(payment.amount for payment in self.payments.values())

    def calculate_total_amount_paid(self) -> NonNegativeFloat:
        return sum(payment.amount for payment in self.payments.values() if payment.status == PaymentStatus.PAID)

    def calculate_total_amount_pending(self) -> NonNegativeFloat:
        return sum(payment.amount for payment in self.payments.values() if payment.status == PaymentStatus.PENDING)

    def change_payment_status(self, payment_id: PositiveInt, status: PaymentStatus) -> None:
        self.payments[payment_id].change_status(status)

    def __len__(self) -> int:
        return len(self.payments)

    @classmethod
    def _private_attributes(cls):
        return set(("payments",))

    @classmethod
    def get_fields_and_types(cls):
        return {
            field: field_info
            for field, field_info in cls.model_fields.items()
            if field not in cls._private_attributes()
        }


class PaymentFactory:
    @staticmethod
    def create_payment(
        amount: NonNegativeFloat,
        end_date: datetime,
        id: int,
        status: Optional[PaymentStatus] = None,
    ) -> Payment:
        if status is None:
            status = PaymentStatus.PENDING
        return Payment(id=id, amount=amount, end_date=end_date, status=status)


class PaymentListFactory:
    @staticmethod
    def create_payment_list(
        dinero_total_prestado: float,
        tasa_interes: float,
        pago_mensual: float,
        fecha_inicio: datetime,
        num_pagos: int,
        moneda: Currency,
        ids: Optional[list[int]] = None,
    ) -> PaymentList:
        if ids is None:
            ids = list(range(1, num_pagos + 1))

        list_payments = {
            identifier: PaymentFactory.create_payment(
                amount=pago_mensual,
                end_date=fecha_inicio + relativedelta(months=i),
                status=PaymentStatus.PENDING,
                id=identifier,
            )
            for i, identifier in zip(range(num_pagos), ids)
        }
        return PaymentList(
            payments=list_payments,
            num_pagos=num_pagos,
            fecha_inicio=fecha_inicio,
            dinero_total_prestado=dinero_total_prestado,
            tasa_interes=tasa_interes,
            pago_mensual=pago_mensual,
            moneda=moneda,
        )

    
    @staticmethod
    def create_from_payment_list_record_dict(payment_record_dict: dict) -> PaymentList:
        return PaymentList(
            fecha_inicio=payment_record_dict["fecha_inicio"],
            pago_mensual=payment_record_dict["pago_mensual"],
            num_pagos=payment_record_dict["num_pagos"],
            dinero_total_prestado=payment_record_dict["dinero_total_prestado"],
            tasa_interes=payment_record_dict["tasa_interes"],
            moneda=payment_record_dict["moneda"],
            payments=payment_record_dict["payments"],
        )

    
    @staticmethod
    def create_from_payment_list_record_str(payment_record_str: str) -> PaymentList:
        payment_record_dict = json.loads(payment_record_str)
        return PaymentList(
            fecha_inicio=payment_record_dict["fecha_inicio"],
            pago_mensual=payment_record_dict["pago_mensual"],
            num_pagos=payment_record_dict["num_pagos"],
            dinero_total_prestado=payment_record_dict["dinero_total_prestado"],
            tasa_interes=payment_record_dict["tasa_interes"],
            moneda=payment_record_dict["moneda"],
            payments=payment_record_dict["payments"],
        )
