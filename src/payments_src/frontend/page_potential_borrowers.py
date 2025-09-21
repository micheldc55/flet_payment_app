import os
import uuid

import streamlit as st

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.db.csv_db.db_operations import (
    append_customers_table,
    append_potential_customers_table,
    edit_potential_customers_table_record,
    read_customers_table,
    read_dealership_table,
    read_potential_customers_filtering_columns,
    read_potential_customers_table,
    write_customers_table,
    write_potential_customers_table,
)
from payments_src.domain.borrower_enums import PotentialBorrowerStatus
from payments_src.domain.borrowers import BorrowerFactory
from payments_src.domain.car import Car
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.domain.loans import LoanFactory
from payments_src.domain.payments import PaymentListFactory
from payments_src.domain.potential_borrowers import PotentialBorrower
from payments_src.frontend.enums.enums_potential_borrowers import PagePotentialBorrowersActions, PotentialBorrowersTitle
from payments_src.frontend.utils import add_n_line_jumps
from payments_src.shared.pydantic_validation_utils import (
    get_field_input_widget_car,
    get_field_input_widget_dealership,
    get_field_input_widget_potential_borrower,
)


def add_loan_page():
    with st.form("add_loan_form", clear_on_submit=True, enter_to_submit=False):
        st.write("Formulario para agregar un nuevo credito")

        borrower_fields = PotentialBorrower.get_fields_and_types()
        car_fields = Car.get_fields_and_types()
        dealership_fields = Dealership.get_fields_and_types()

        borrower_form_data = {}
        car_form_data = {}
        dealership_form_data = {}

        form_data = {"borrower": borrower_form_data, "car": car_form_data, "dealership": dealership_form_data}

        st.subheader("Datos del Cliente")
        for field_name, field_info in borrower_fields.items():
            # Skip internal Pydantic fields if any
            if field_name.startswith("_"):
                continue

            field_value = get_field_input_widget_potential_borrower(
                field_name=field_name, field_info=field_info, key=f"form_{field_name}"
            )

            borrower_form_data[field_name] = field_value

            st.caption(f"Tipo de dato: {field_info.annotation.__name__}")

        st.subheader("Datos del Vehiculo")
        for field_name, field_info in car_fields.items():
            if field_name.startswith("_"):
                continue

            field_value = get_field_input_widget_car(
                field_name=field_name, field_info=field_info, key=f"form_{field_name}"
            )

            car_form_data[field_name] = field_value

            st.caption(f"Tipo de dato: {field_info.annotation.__name__}")

        st.subheader("Automotora")

        dealership_table = read_dealership_table()

        dealership_table["display_name"] = (
            dealership_table["dealership_id"].astype(str) + " - " + dealership_table["name"]
        )
        dealership_list = dealership_table["display_name"].tolist()
        dealership_list = [None] + dealership_list

        st.selectbox("Selecciona una automotora", dealership_list, index=0, key="dealership_selectbox")

        st.subheader("Subir Archivos")

        files = st.file_uploader("Subir archivos", type=["pdf", "jpg", "jpeg", "png"], key="files_uploader")
        if (files is not None) and (not isinstance(files, list)):
            files = [files]

        add_n_line_jumps(2)
        submitted = st.form_submit_button("Agregar Credito")

        if submitted:
            potential_customers_table = read_potential_customers_table()
            if len(potential_customers_table) == 0:
                next_id = 1
            else:
                next_id = potential_customers_table["borrower_id"].astype(int).max() + 1
            borrower_form_data["borrower_id"] = next_id

            # create a new directory for the new user in the database
            new_directory = os.path.join(CSVTable.CUSTOMER_FILES_PATH.value, str(borrower_form_data["borrower_id"]))
            os.makedirs(new_directory, exist_ok=False)

            borrower_form_data["path_to_files"] = new_directory
            borrower_form_data["status"] = PotentialBorrowerStatus.POTENTIAL.value

            car_form_data["borrower_id"] = borrower_form_data["borrower_id"]

            new_borrower = PotentialBorrower(**borrower_form_data)

            if files is not None:
                for file in files:
                    file_name = file.name
                    file_path = os.path.join(new_directory, file_name)
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())

            # save the new_borrower to the database
            potential_customers_table = read_potential_customers_table()
            potential_customers_table = append_potential_customers_table(potential_customers_table, new_borrower)
            write_potential_customers_table(potential_customers_table, overwrite=True)
            st.success(f"Préstamo agregado exitosamente! ID: {new_borrower.borrower_id}")


def view_loan_page():
    potential_customers_table = read_potential_customers_table()

    display_df = potential_customers_table.copy()
    display_df["display_name"] = display_df["borrower_id"].astype(str) + " - " + display_df["nombre_cliente"]

    borrower_list = display_df["display_name"].tolist()
    mapping_borrower_id_to_display_name = dict(zip(display_df["display_name"], display_df["borrower_id"]))

    short_col, _ = st.columns([1, 4])
    borrower_display_name = short_col.selectbox("Selecciona un credito", borrower_list)

    borrower_id = mapping_borrower_id_to_display_name[borrower_display_name]
    potential_borrower_data = potential_customers_table[potential_customers_table["borrower_id"] == borrower_id].iloc[0]
    potential_borrower = PotentialBorrower(**potential_borrower_data)

    st.dataframe(potential_borrower.to_printable_dataframe())

    col1, col2, _ = st.columns([1, 1, 7])

    # if status is pending show approve/reject else show only reject
    if potential_borrower.status == PotentialBorrowerStatus.POTENTIAL.value:
        approve_loan = col1.button("Aprobar")
        reject_loan = col2.button("Rechazar")
    else:
        approve_loan = None
        reject_loan = col1.button("Rechazar")

    if approve_loan:
        potential_borrower.approve_loan()
        potential_customers_table = read_potential_customers_table()
        potential_customers_table = edit_potential_customers_table_record(potential_customers_table, potential_borrower)
        write_potential_customers_table(potential_customers_table, overwrite=True)

        borrower = potential_borrower.create_borrower_from_potential_borrower()
        customers_table = read_customers_table()
        customers_table = append_customers_table(customers_table, borrower)
        write_customers_table(customers_table, overwrite=True)

        st.success(f"Préstamo aprobado exitosamente! ID: {borrower.borrower_id} | Nombre: {borrower.nombre_cliente}")

    if reject_loan:
        potential_borrower.reject_loan()
        potential_customers_table = read_potential_customers_table()
        potential_customers_table = edit_potential_customers_table_record(potential_customers_table, potential_borrower)
        write_potential_customers_table(potential_customers_table, overwrite=True)
        st.warning(
            f"Préstamo Rechazado. ID: {potential_borrower.borrower_id} | Nombre: {potential_borrower.nombre_cliente}"
        )


def edit_loan_page():
    pass


def potential_borrowers_page():
    st.title(PotentialBorrowersTitle.TITLE.value)
    st.subheader(PotentialBorrowersTitle.SUBTITLE.value)

    add_n_line_jumps(2)

    short_col, _ = st.columns([1, 4])

    selected_action = short_col.selectbox(
        "Selecciona una acción", PagePotentialBorrowersActions.list(), index=0, key="potential_borrowers_action"
    )

    if selected_action == PagePotentialBorrowersActions.LIST_LOANS.value:
        potential_customers_table = read_potential_customers_filtering_columns(
            PotentialBorrower.get_displayable_columns()
        )
        st.dataframe(potential_customers_table)

    elif selected_action == PagePotentialBorrowersActions.ADD_LOAN.value:
        add_loan_page()

    elif selected_action == PagePotentialBorrowersActions.VIEW_LOAN.value:
        view_loan_page()

    elif selected_action == PagePotentialBorrowersActions.EDIT_LOAN.value:
        pass
