import os

from payments_src.db.csv_db.db_constants import CSVTable


def remove_list_of_files(list_of_files: list[str]) -> None:
    for file in list_of_files:
        if not os.path.abspath(file).startswith(os.path.abspath(CSVTable.PATH.value)):
            raise ValueError(f"The only files that can be eliminated using this function are in the src/payments_src/db/csv_db directory. File {file} is not in src/payments_src/db/csv_db directory")

        if os.path.exists(file):
            os.remove(file)
        else:
            raise FileNotFoundError(f"File {file} not found")
