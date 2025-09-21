import pydantic
import pytest

from payments_src.domain.borrowers import Borrower, BorrowerFactory


def test_borrower():
    borrower = Borrower(
        borrower_id=12345678,
        nombre_cliente="John",
        telefono_cliente="1234567890",
        notas="No notes",
        path_to_files="path/to/files",
    )
    assert borrower.borrower_id == 12345678
    assert borrower.nombre_cliente == "John"
    assert borrower.telefono_cliente == "1234567890"
    assert borrower.notas == "No notes"
    assert borrower.path_to_files == "path/to/files"


def test_borrower_raises_validation_error():
    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=-12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
        )

    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=12345678,
            nombre_cliente=12345678,
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
        )

    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente=1234567890,
            notas="No notes",
            path_to_files="path/to/files",
        )

    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas=123456,
            path_to_files="path/to/files",
        )

    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=0,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files="path/to/files",
        )

    with pytest.raises(pydantic.ValidationError):
        Borrower(
            borrower_id=12345678,
            nombre_cliente="John",
            telefono_cliente="1234567890",
            notas="No notes",
            path_to_files=123456,
        )


def test_factory_create_borrower():
    borrower = BorrowerFactory.create_borrower(
        borrower_id=12345678,
        name="John",
        phone_number="1234567890",
        notes="No notes",
        path_to_files="path/to/files",
    )
    assert borrower.borrower_id == 12345678
    assert borrower.nombre_cliente == "John"
    assert borrower.telefono_cliente == "1234567890"
    assert borrower.notas == "No notes"
    assert borrower.path_to_files == "path/to/files"
