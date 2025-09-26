import os

import streamlit as st
import pandas as pd

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.db.csv_db.db_operations import (
    append_customers_table,
    read_customers_table,
    read_dealership_table,
    write_customers_table,
    read_loan_table,
    append_loan_table,
    write_loan_table,
    read_and_expand_loans_table,
    edit_loan_table_record
)
from payments_src.domain.borrowers import Borrower, BorrowerFactory
from payments_src.domain.car import Car, CarFactory
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.domain.loans import LoanFactory, Loan
from payments_src.domain.loans_enums import LoanStatus
from payments_src.domain.payment_enums import Currency
from payments_src.domain.payments import PaymentListFactory, PaymentList
from payments_src.frontend.enums.enums_potential_borrowers import PagePotentialBorrowersActions, PotentialBorrowersTitle
from payments_src.frontend.utils import add_n_line_jumps
from payments_src.operations.loans.loan_number_calculations import get_next_loan_readable_number, get_next_loan_id, get_next_borrower_id
from payments_src.shared.pydantic_validation_utils import (
    get_field_input_widget_car,
    get_field_input_widget_potential_borrower,
    get_field_input_widget_payment_list,
)


def pretty_print_object(class_instance: object) -> None:
    properties = [field_name for field_name in class_instance.get_fields_and_types().keys()]
    values = [
        getattr(class_instance, field_name).value if isinstance(getattr(class_instance, field_name), Currency) else getattr(class_instance, field_name)
        for field_name in properties
    ]
    
    display_df = pd.DataFrame({"propiedad": properties, "valor": values})

    wide_col, _ = st.columns([1, 1])
    wide_col.dataframe(display_df)


def list_loans_page():
    st.subheader("Mostrando todos los préstamos pendientes de aprobación")

    loans_table_copy = read_and_expand_loans_table()

    if loans_table_copy.empty:
        st.warning("No hay préstamos potenciales para mostrar")
        return
    
    expanded_df = loans_table_copy[["loan_id", "loan_readable_code", "status"]]

    borrower_fields = Borrower.get_fields_and_types()
    for field_name in borrower_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["borrower"].apply(lambda x: getattr(x, field_name))
    
    car_fields = Car.get_fields_and_types()
    for field_name in car_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["car"].apply(lambda x: getattr(x, field_name))
    
    dealership_fields = Dealership.get_fields_and_types()
    for field_name in dealership_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["dealership"].apply(lambda x: getattr(x, field_name))
    
    payment_list_fields = PaymentList.get_fields_and_types()
    for field_name in payment_list_fields.keys():
        expanded_df[f"{field_name}"] = loans_table_copy["payment_list"].apply(
            lambda x: getattr(x, field_name).value if isinstance(getattr(x, field_name), Currency) else getattr(x, field_name)
        )
    
    st.dataframe(expanded_df)


def add_loan_page():
    with st.form("add_loan_form", clear_on_submit=True, enter_to_submit=False):
        st.write("Formulario para agregar un nuevo credito")

        car_fields = Car.get_fields_and_types()
        dealership_fields = Dealership.get_fields_and_types()
        borrower_fields = Borrower.get_fields_and_types()

        borrower_form_data = {}
        car_form_data = {}
        dealership_form_data = {}
        payment_list_form_data = {}

        form_data = {"borrower": borrower_form_data, "car": car_form_data, "dealership": dealership_form_data, "payment_list": payment_list_form_data}


        st.subheader("Datos del Cliente")
        for field_name, field_info in borrower_fields.items():
            # Skip internal Pydantic fields if any
            if field_name.startswith("_"):
                continue

            field_value = get_field_input_widget_potential_borrower(
                field_name=field_name, field_info=field_info, key=f"form_{field_name}"
            )
            # Normalize the field value: if it's an empty string, coerce to None
            field_value = field_value or None

            borrower_form_data[field_name] = field_value

            st.caption(f"Tipo de dato: {field_info.annotation.__name__}")


        st.subheader("Datos del Vehiculo")
        for field_name, field_info in car_fields.items():
            if field_name.startswith("_"):
                continue

            field_value = get_field_input_widget_car(
                field_name=field_name, field_info=field_info, key=f"form_{field_name}"
            )
            # Normalize the field value: if it's an empty string, coerce to None
            field_value = field_value or None

            car_form_data[field_name] = field_value

            st.caption(f"Tipo de dato: {field_info.annotation.__name__}")


        st.subheader("Automotora")

        dealership_table = read_dealership_table()
        dealership_table_copy = dealership_table.copy()

        dealership_table_copy["display_name"] = (
            dealership_table_copy["dealership_id"].astype(str) + " - " + dealership_table_copy["name"]
        )
        dealership_list = dealership_table_copy["display_name"].tolist()
        dealership_list = [None] + dealership_list

        selected_dealership = st.selectbox("Selecciona una automotora", dealership_list, index=0, key="dealership_selectbox")

        
        st.subheader("Datos de la Financiación")

        payment_list_fields = PaymentList.get_fields_and_types()

        for field_name, field_info in payment_list_fields.items():
            if field_name.startswith("_"):
                continue
            field_value = get_field_input_widget_payment_list(field_name=field_name, field_info=field_info, key=f"form_{field_name}")
            field_value = field_value or None
            payment_list_form_data[field_name] = field_value
        
        
        st.subheader("Subir Archivos")

        files = st.file_uploader("Subir archivos", type=["pdf", "jpg", "jpeg", "png"], key="files_uploader")
        if (files is not None) and (not isinstance(files, list)):
            files = [files]

        add_n_line_jumps(2)
        submitted = st.form_submit_button("Agregar Credito")

        if submitted:
            if selected_dealership is None:
                st.error("Debe seleccionar una automotora para continuar!")
                raise ValueError("Debe seleccionar una automotora para continuar!")

            borrower_form_data["borrower_id"] = get_next_borrower_id()

            # create a new directory for the new user in the database
            new_directory = os.path.join(CSVTable.CUSTOMER_FILES_PATH.value, str(borrower_form_data["borrower_id"]))

            borrower_form_data["path_to_files"] = new_directory

            car_form_data["borrower_id"] = borrower_form_data["borrower_id"]
            
            selected_dealership_dict = dealership_table[dealership_table_copy["display_name"] == selected_dealership].iloc[0].to_dict()

            new_borrower = Borrower(**borrower_form_data)
            new_car = Car(**car_form_data)
            dealership = Dealership(**selected_dealership_dict)
            payment_list = PaymentListFactory.create_payment_list(**payment_list_form_data)

            loan_number = get_next_loan_readable_number(dealership.dealership_id)

            borrower_table = read_customers_table()
            loan_table = read_loan_table()

            # create a new loan with Pending status (default)
            new_loan = LoanFactory.create_loan(
                loan_id=get_next_loan_id(),
                loan_number=loan_number,
                payment_list=payment_list,
                borrower=new_borrower,
                car=new_car,
                dealership=dealership,
                status=LoanStatus.POTENTIAL,
            )

            os.makedirs(new_directory, exist_ok=False)

            if files is not None:
                for file in files:
                    file_name = file.name
                    file_path = os.path.join(new_directory, file_name)
                    with open(file_path, "wb") as f:
                        f.write(file.getvalue())

            # save the new borrower to the database
            borrower_table = append_customers_table(borrower_table, new_borrower)
            write_customers_table(borrower_table, overwrite=True)
            
            # save the new loan to the database
            loan_table = append_loan_table(loan_table, new_loan)
            write_loan_table(loan_table, overwrite=True)
            st.success(f"Préstamo agregado exitosamente! ID: {new_borrower.borrower_id}")


def view_loan_page():
    loans_table_copy = read_and_expand_loans_table()

    if loans_table_copy.empty:
        st.warning("No hay préstamos pendientes que mostrar")

        return

    loans_table_copy["display_name"] = loans_table_copy.apply(
        lambda x: 
            str(x["loan_id"]) + " - " 
            + x["loan_readable_code"] + " - " 
            + x["borrower"].nombre_cliente + f' ({x["car"].marca_auto} {x["car"].modelo_auto})',
        axis=1
    )

    display_series = loans_table_copy["display_name"]

    borrower_list = display_series.tolist()
    mapping_borrower_id_to_display_name = dict(zip(display_series, loans_table_copy["loan_id"]))

    short_col, _ = st.columns([1, 2])
    borrower_display_name = short_col.selectbox("Selecciona un credito", borrower_list)


    loan_id = mapping_borrower_id_to_display_name[borrower_display_name]
    loan = loans_table_copy[loans_table_copy["loan_id"] == loan_id].iloc[0]
    loan_obj = Loan(**loan.to_dict())

    st.subheader("Cliente")
    pretty_print_object(loan_obj.borrower)
    st.subheader("Vehiculo")
    pretty_print_object(loan_obj.car)
    st.subheader("Automotora")
    pretty_print_object(loan_obj.dealership)
    st.subheader("Financiación")
    pretty_print_object(loan_obj.payment_list)

    add_n_line_jumps(2)
    col1, col2, _ = st.columns([1, 1, 7])

    # if status is pending show approve/reject else show only reject
    if loan_obj.status == LoanStatus.POTENTIAL.value:
        approve_loan = col1.button("Aprobar")
        reject_loan = col2.button("Rechazar")
    else:
        approve_loan = None
        reject_loan = col1.button("Rechazar")

    if approve_loan:
        loan_obj.approve_loan()
        clean_loan_table = read_loan_table()
        clean_loan_table = edit_loan_table_record(clean_loan_table, loan_obj)
        write_loan_table(clean_loan_table, overwrite=True)

        st.success(f"Préstamo Aprobado! ID Financiación: {loan_obj.loan_id} | ID Cliente {loan_obj.borrower.borrower_id} | Nombre: {loan_obj.borrower.nombre_cliente}")

    if reject_loan:
        loan_obj.reject_loan()
        clean_loan_table = read_loan_table()
        clean_loan_table = edit_loan_table_record(clean_loan_table, loan_obj)
        write_loan_table(clean_loan_table, overwrite=True)
        st.warning(
            f"Préstamo Rechazado! ID Financiación: {loan_obj.loan_id} | ID Cliente {loan_obj.borrower.borrower_id} | Nombre: {loan_obj.borrower.nombre_cliente}"
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
        list_loans_page()

    elif selected_action == PagePotentialBorrowersActions.ADD_LOAN.value:
        add_loan_page()

    elif selected_action == PagePotentialBorrowersActions.VIEW_LOAN.value:
        view_loan_page()

    elif selected_action == PagePotentialBorrowersActions.EDIT_LOAN.value:
        pass
