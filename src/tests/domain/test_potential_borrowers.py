import pydantic
import pytest

from payments_src.domain.potential_borrowers import PotentialBorrower
from payments_src.domain.borrower_enums import PotentialBorrowerStatus


def test_borrower():
    borrower = PotentialBorrower(
        borrower_id=12345678,
        nombre_cliente="John",
        telefono_cliente="1234567890",
        notas="No notes",
        path_to_files="path/to/files",
        status=PotentialBorrowerStatus.POTENTIAL.value,
    )
    assert borrower.borrower_id == 12345678
    assert borrower.nombre_cliente == "John"
    assert borrower.telefono_cliente == "1234567890"
    assert borrower.notas == "No notes"
    assert borrower.path_to_files == "path/to/files"
    assert borrower.status == PotentialBorrowerStatus.POTENTIAL.value

def test_borrower_raises_validation_error():
    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=-12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=12345678,
            nombre_cliente=12345678,
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente=1234567890,
            notas="No notes",
            path_to_files="path/to/files",
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas=123456,
            path_to_files="path/to/files",
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=0,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files=123456,
            status=PotentialBorrowerStatus.POTENTIAL.value,
        )

    with pytest.raises(pydantic.ValidationError):
        PotentialBorrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
            status="pending",
        )