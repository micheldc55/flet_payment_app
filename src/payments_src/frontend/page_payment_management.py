import streamlit as st
from datetime import datetime
import pandas as pd

from payments_src.frontend.enums.enums_payment_management import PaymentManagementActions, PaymentFilterType
from payments_src.db.csv_db.db_operations import read_and_expand_loans_table, edit_loan_table_record, read_loan_table, write_loan_table
from payments_src.domain.loans_enums import LoanStatus
from payments_src.domain.payment_enums import PaymentStatus
from payments_src.domain.loans import Loan
from payments_src.frontend.utils import add_n_line_jumps


def payment_management_page():
    st.title("Gestión de Pagos")
    
    # Action selection
    st.write("Selecciona la acción que deseas realizar. Puedes elegir entre:")
    st.write("• **Marcar pago como pagado**: Marcar pagos individuales o por mes como pagados.")
    st.write("• **Editar pago**: Editar datos depagos individuales o por mes. Podrás modificar el monto, la fecha de vencimiento y la fecha de pago.")
    st.write("• **Ver pagos**: Ver pagos individuales o por mes. También podrás generar reportes de pagos.")
    add_n_line_jumps(1)
    short_col, _ = st.columns([1, 3])
    selected_action = short_col.selectbox(
        "Selecciona una acción", 
        PaymentManagementActions.list(), 
        index=0, 
        key="payment_management_action"
    )
    
    if selected_action == PaymentManagementActions.MARK_AS_PAID.value:
        mark_payment_as_paid_section()
    elif selected_action == PaymentManagementActions.EDIT_PAYMENT.value:
        edit_payment_section()
    elif selected_action == PaymentManagementActions.VIEW_PAYMENTS.value:
        view_payments_section()


def mark_payment_as_paid_section():
    st.header("Marcar Pago como Pagado")
    
    # Filter type selection
    filter_col, _ = st.columns([1, 2])
    filter_type = filter_col.selectbox(
        "Filtrar por:",
        PaymentFilterType.list(),
        key="mark_paid_filter_type"
    )
    
    # Get active loans
    active_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
    
    if filter_type == PaymentFilterType.BY_BORROWER.value:
        mark_payment_by_borrower(active_loans_df)
    else:  # BY_MONTH
        mark_payment_by_month(active_loans_df)


def mark_payment_by_borrower(active_loans_df):
    # Create display names for borrowers
    active_loans_df["display_name"] = active_loans_df.apply(
        lambda x: f"{x['loan_id']} - {x['loan_readable_code']} - {x['borrower'].nombre_cliente} ({x['car'].marca_auto} {x['car'].modelo_auto})",
        axis=1
    )
    
    # Borrower selection
    st.subheader("Selecciona un Cliente")
    borrower_display_names = active_loans_df["display_name"].tolist()
    selected_borrower = st.selectbox(
        "Cliente:",
        borrower_display_names,
        key="mark_paid_borrower"
    )
    
    # Get selected loan
    loan_id = active_loans_df[active_loans_df["display_name"] == selected_borrower]["loan_id"].iloc[0]
    selected_loan_row = active_loans_df[active_loans_df["loan_id"] == loan_id].iloc[0]

    selected_loan = Loan(**selected_loan_row.to_dict())
    
    # Display pending payments
    st.subheader("Pagos Pendientes")
    pending_payments = [
        payment for payment in selected_loan.payment_list.payments.values() 
        if payment.status == PaymentStatus.PENDING.value
    ]
    
    if not pending_payments:
        st.info("No hay pagos pendientes para este cliente.")
        return
    
    # Create payment selection
    payment_options = []
    for payment in pending_payments:
        payment_options.append(f"Pago #{payment.id} - ${payment.amount:.2f} - Vence: {payment.end_date.strftime('%Y-%m-%d')}")
    
    selected_payment_option = st.selectbox(
        "Selecciona un pago para marcar como pagado:",
        payment_options,
        key="mark_paid_payment_selection"
    )
    
    # Get selected payment ID
    selected_payment_id = int(selected_payment_option.split("Pago #")[1].split(" -")[0])
    
    # Payment date input
    payment_date = st.date_input(
        "Fecha de pago:",
        value=datetime.now().date(),
        key="mark_paid_date"
    )
    
    # Confirm button
    if st.button("Marcar como Pagado", key="mark_paid_confirm"):
        # Update payment status
        selected_loan.payment_list.payments[selected_payment_id].change_status(PaymentStatus.PAID)
        selected_loan.payment_list.payments[selected_payment_id].change_date_paid(datetime.combine(payment_date, datetime.min.time()))
        
        # Update loan in database
        loans_df = read_loan_table()
        updated_loans_df = edit_loan_table_record(loans_df, selected_loan)
        write_loan_table(updated_loans_df, overwrite=True)
        
        st.success(f"Pago #{selected_payment_id} marcado como pagado exitosamente!")
        st.rerun()


def mark_payment_by_month(active_loans_df):
    st.subheader("Selecciona un Mes")
    
    # Get all unique months from payment end dates
    all_months = set()
    for _, loan_row in active_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            month_key = payment.end_date.strftime('%Y-%m')
            all_months.add(month_key)
    
    if not all_months:
        st.info("No hay pagos disponibles.")
        return
    
    # Month selection
    sorted_months = sorted(list(all_months))
    selected_month = st.selectbox(
        "Mes:",
        sorted_months,
        key="mark_paid_month"
    )
    
    # Collect payments for selected month
    pending_payments = []
    paid_payments = []
    
    for _, loan_row in active_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            if payment.end_date.strftime('%Y-%m') == selected_month:
                payment_info = {
                    'loan_id': loan.loan_id,
                    'loan_code': loan.loan_readable_code,
                    'borrower_name': loan.borrower.nombre_cliente,
                    'car_info': f"{loan.car.marca_auto} {loan.car.modelo_auto}",
                    'payment_id': payment.id,
                    'amount': payment.amount,
                    'end_date': payment.end_date,
                    'status': payment.status,
                    'date_paid': payment.date_paid,
                    'payment_obj': payment,
                    'loan_obj': loan
                }
                
                if payment.status == PaymentStatus.PENDING.value:
                    pending_payments.append(payment_info)
                else:
                    paid_payments.append(payment_info)
    
    # Display pending payments table
    st.subheader("Pagos Pendientes")
    if pending_payments:
        pending_df = pd.DataFrame([
            {
                'ID Préstamo': p['loan_id'],
                'Código': p['loan_code'],
                'Cliente': p['borrower_name'],
                'Vehículo': p['car_info'],
                'Pago #': p['payment_id'],
                'Monto': f"${p['amount']:.2f}",
                'Vence': p['end_date'].strftime('%Y-%m-%d')
            }
            for p in pending_payments
        ])
        st.dataframe(pending_df, use_container_width=True)
        
        # Payment selection for marking as paid
        payment_options = []
        for p in pending_payments:
            payment_options.append(f"Préstamo {p['loan_id']} - Pago #{p['payment_id']} - {p['borrower_name']} - ${p['amount']:.2f}")
        
        selected_payment_option = st.selectbox(
            "Selecciona un pago para marcar como pagado:",
            payment_options,
            key="mark_paid_month_payment_selection"
        )
        
        # Get selected payment info
        selected_payment_info = None
        for p in pending_payments:
            if f"Préstamo {p['loan_id']} - Pago #{p['payment_id']} - {p['borrower_name']} - ${p['amount']:.2f}" == selected_payment_option:
                selected_payment_info = p
                break
        
        if selected_payment_info:
            # Payment date input
            payment_date = st.date_input(
                "Fecha de pago:",
                value=datetime.now().date(),
                key="mark_paid_month_date"
            )
            
            # Confirm button
            if st.button("Marcar como Pagado", key="mark_paid_month_confirm"):
                # Update payment status
                loan = selected_payment_info['loan_obj']
                payment_id = selected_payment_info['payment_id']
                loan.payment_list.payments[payment_id].change_status(PaymentStatus.PAID)
                loan.payment_list.payments[payment_id].change_date_paid(datetime.combine(payment_date, datetime.min.time()))
                
                # Update loan in database
                loans_df = read_loan_table()
                updated_loans_df = edit_loan_table_record(loans_df, loan)
                write_loan_table(updated_loans_df, overwrite=True)
                
                st.success(f"Pago #{payment_id} marcado como pagado exitosamente!")
                st.rerun()
    else:
        st.info("No hay pagos pendientes para este mes.")
    
    # Display paid payments table
    st.subheader("Pagos Realizados")
    if paid_payments:
        paid_df = pd.DataFrame([
            {
                'ID Préstamo': p['loan_id'],
                'Código': p['loan_code'],
                'Cliente': p['borrower_name'],
                'Vehículo': p['car_info'],
                'Pago #': p['payment_id'],
                'Monto': f"${p['amount']:.2f}",
                'Vence': p['end_date'].strftime('%Y-%m-%d'),
                'Pagado': p['date_paid'].strftime('%Y-%m-%d') if p['date_paid'] else 'N/A'
            }
            for p in paid_payments
        ])
        st.dataframe(paid_df, use_container_width=True)
    else:
        st.info("No hay pagos realizados para este mes.")


def edit_payment_section():
    st.header("Editar Pago")
    
    # Filter type selection
    filter_col, _ = st.columns([1, 2])
    filter_type = filter_col.selectbox(
        "Filtrar por:",
        PaymentFilterType.list(),
        key="edit_payment_filter_type"
    )
    
    # Get active loans
    active_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
    
    if filter_type == PaymentFilterType.BY_BORROWER.value:
        edit_payment_by_borrower(active_loans_df)
    else:  # BY_MONTH
        edit_payment_by_month(active_loans_df)


def edit_payment_by_borrower(active_loans_df):
    # Create display names for borrowers
    active_loans_df["display_name"] = active_loans_df.apply(
        lambda x: f"{x['loan_id']} - {x['loan_readable_code']} - {x['borrower'].nombre_cliente} ({x['car'].marca_auto} {x['car'].modelo_auto})",
        axis=1
    )
    
    # Borrower selection
    st.subheader("Selecciona un Cliente")
    borrower_display_names = active_loans_df["display_name"].tolist()
    selected_borrower = st.selectbox(
        "Cliente:",
        borrower_display_names,
        key="edit_payment_borrower"
    )
    
    # Get selected loan
    loan_id = active_loans_df[active_loans_df["display_name"] == selected_borrower]["loan_id"].iloc[0]
    selected_loan_row = active_loans_df[active_loans_df["loan_id"] == loan_id].iloc[0]
    selected_loan = Loan(**selected_loan_row.to_dict())
    
    # Display all payments
    st.subheader("Pagos del Cliente")
    all_payments = list(selected_loan.payment_list.payments.values())
    
    if not all_payments:
        st.info("No hay pagos para este cliente.")
        return
    
    # Create payment selection
    payment_options = []
    for payment in all_payments:
        status_text = "Pagado" if payment.status == PaymentStatus.PAID.value else "Pendiente"
        payment_options.append(f"Pago #{payment.id} - ${payment.amount:.2f} - {status_text} - Vence: {payment.end_date.strftime('%Y-%m-%d')}")
    
    selected_payment_option = st.selectbox(
        "Selecciona un pago para editar:",
        payment_options,
        key="edit_payment_selection"
    )
    
    # Get selected payment ID
    selected_payment_id = int(selected_payment_option.split("Pago #")[1].split(" -")[0])
    selected_payment = selected_loan.payment_list.payments[selected_payment_id]
    
    # Edit form
    st.subheader("Editar Pago")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_amount = st.number_input(
            "Nuevo monto:",
            value=float(selected_payment.amount),
            min_value=0.0,
            step=0.01,
            key="edit_payment_amount"
        )
        
        new_end_date = st.date_input(
            "Nueva fecha de vencimiento:",
            value=selected_payment.end_date.date(),
            key="edit_payment_end_date"
        )
    
    with col2:
        if selected_payment.status == PaymentStatus.PAID.value and selected_payment.date_paid:
            new_payment_date = st.date_input(
                "Nueva fecha de pago:",
                value=selected_payment.date_paid.date(),
                key="edit_payment_payment_date"
            )
        else:
            new_payment_date = None
    
    # Confirm button
    if st.button("Guardar Cambios", key="edit_payment_confirm"):
        # Update payment
        selected_payment.change_amount(new_amount)
        selected_payment.change_end_date(datetime.combine(new_end_date, datetime.min.time()))
        
        if new_payment_date:
            selected_payment.change_date_paid(datetime.combine(new_payment_date, datetime.min.time()))
        
        # Update loan in database
        loans_df = read_loan_table()
        updated_loans_df = edit_loan_table_record(loans_df, selected_loan)
        write_loan_table(updated_loans_df, overwrite=True)
        
        st.success(f"Pago #{selected_payment_id} actualizado exitosamente!")
        st.rerun()


def edit_payment_by_month(active_loans_df):
    st.subheader("Selecciona un Mes")
    
    # Get all unique months from payment end dates
    all_months = set()
    for _, loan_row in active_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            month_key = payment.end_date.strftime('%Y-%m')
            all_months.add(month_key)
    
    if not all_months:
        st.info("No hay pagos disponibles.")
        return
    
    # Month selection
    sorted_months = sorted(list(all_months))
    selected_month = st.selectbox(
        "Mes:",
        sorted_months,
        key="edit_payment_month"
    )
    
    # Collect payments for selected month
    all_payments = []
    
    for _, loan_row in active_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            if payment.end_date.strftime('%Y-%m') == selected_month:
                payment_info = {
                    'loan_id': loan.loan_id,
                    'loan_code': loan.loan_readable_code,
                    'borrower_name': loan.borrower.nombre_cliente,
                    'borrower_phone': loan.borrower.telefono_cliente,
                    'car_info': f"{loan.car.marca_auto} {loan.car.modelo_auto}",
                    'payment_id': payment.id,
                    'amount': payment.amount,
                    'end_date': payment.end_date,
                    'status': payment.status,
                    'date_paid': payment.date_paid,
                    'payment_obj': payment,
                    'loan_obj': loan
                }
                all_payments.append(payment_info)
    
    if not all_payments:
        st.info("No hay pagos para este mes.")
        return
    
    # Display payments table
    st.subheader("Pagos del Mes")
    payments_df = pd.DataFrame([
        {
            'ID Préstamo': p['loan_id'],
            'Código': p['loan_code'],
            'Cliente': p['borrower_name'],
            'Teléfono': p['borrower_phone'],
            'Vehículo': p['car_info'],
            'Pago #': p['payment_id'],
            'Monto': f"${p['amount']:.2f}",
            'Estado': "Pagado" if p['status'] == PaymentStatus.PAID.value else "Pendiente",
            'Vence': p['end_date'].strftime('%Y-%m-%d'),
            'Pagado': p['date_paid'].strftime('%Y-%m-%d') if p['date_paid'] else 'N/A'
        }
        for p in all_payments
    ])
    st.dataframe(payments_df, use_container_width=True)
    
    # Payment selection for editing
    payment_options = []
    for p in all_payments:
        status_text = "Pagado" if p['status'] == PaymentStatus.PAID.value else "Pendiente"
        payment_options.append(f"Préstamo {p['loan_id']} - Pago #{p['payment_id']} - {p['borrower_name']} - ${p['amount']:.2f} - {status_text}")
    
    selected_payment_option = st.selectbox(
        "Selecciona un pago para editar:",
        payment_options,
        key="edit_payment_month_selection"
    )
    
    # Get selected payment info
    selected_payment_info = None
    for p in all_payments:
        if f"Préstamo {p['loan_id']} - Pago #{p['payment_id']} - {p['borrower_name']} - ${p['amount']:.2f} - {'Pagado' if p['status'] == PaymentStatus.PAID else 'Pendiente'}" == selected_payment_option:
            selected_payment_info = p
            break
    
    if selected_payment_info:
        # Edit form
        st.subheader("Editar Pago")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_amount = st.number_input(
                "Nuevo monto:",
                value=float(selected_payment_info['amount']),
                min_value=0.0,
                step=0.01,
                key="edit_payment_month_amount"
            )
            
            new_end_date = st.date_input(
                "Nueva fecha de vencimiento:",
                value=selected_payment_info['end_date'].date(),
                key="edit_payment_month_end_date"
            )
        
        with col2:
            if selected_payment_info['status'] == PaymentStatus.PAID and selected_payment_info['date_paid']:
                new_payment_date = st.date_input(
                    "Nueva fecha de pago:",
                    value=selected_payment_info['date_paid'].date(),
                    key="edit_payment_month_payment_date"
                )
            else:
                new_payment_date = None
        
        # Confirm button
        if st.button("Guardar Cambios", key="edit_payment_month_confirm"):
            # Update payment
            loan = selected_payment_info['loan_obj']
            payment_id = selected_payment_info['payment_id']
            payment = loan.payment_list.payments[payment_id]
            
            payment.change_amount(new_amount)
            payment.change_end_date(datetime.combine(new_end_date, datetime.min.time()))
            
            if new_payment_date:
                payment.change_date_paid(datetime.combine(new_payment_date, datetime.min.time()))
            
            # Update loan in database
            loans_df = read_loan_table()
            updated_loans_df = edit_loan_table_record(loans_df, loan)
            write_loan_table(updated_loans_df, overwrite=True)
            
            st.success(f"Pago #{payment_id} actualizado exitosamente!")
            st.rerun()


def view_payments_section():
    st.header("Ver Pagos")
    
    # Filter type selection
    filter_col, _ = st.columns([1, 2])
    filter_type = filter_col.selectbox(
        "Filtrar por:",
        ["Todos los pagos", "Por mes"],
        key="view_payments_filter_type"
    )
    
    # Get active loans
    active_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
    
    # Collect all payments
    all_payments = []
    
    for _, loan_row in active_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            payment_info = {
                'loan_id': loan.loan_id,
                'loan_code': loan.loan_readable_code,
                'borrower_name': loan.borrower.nombre_cliente,
                'borrower_phone': loan.borrower.telefono_cliente,
                'car_info': f"{loan.car.marca_auto} {loan.car.modelo_auto}",
                'payment_id': payment.id,
                'amount': payment.amount,
                'end_date': payment.end_date,
                'status': payment.status,
                'date_paid': payment.date_paid
            }
            all_payments.append(payment_info)
    
    if not all_payments:
        st.info("No hay pagos disponibles.")
        return
    
    if filter_type == "Todos los pagos":
        view_all_payments(all_payments)
    else:  # "Por mes"
        view_payments_by_month(all_payments)


def view_all_payments(all_payments):
    # Create summary statistics
    total_payments = len(all_payments)
    paid_payments = len([p for p in all_payments if p['status'] == PaymentStatus.PAID.value])
    pending_payments = total_payments - paid_payments
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pagos", total_payments)
    with col2:
        st.metric("Pagos Realizados", paid_payments)
    with col3:
        st.metric("Pagos Pendientes", pending_payments)
    
    # Display all payments table
    st.subheader("Todos los Pagos")
    payments_df = pd.DataFrame([
        {
            'ID Préstamo': p['loan_id'],
            'Código': p['loan_code'],
            'Cliente': p['borrower_name'],
            'Vehículo': p['car_info'],
            'Pago #': p['payment_id'],
            'Monto': f"${p['amount']:.2f}",
            'Estado': "Pagado" if p['status'] == PaymentStatus.PAID.value else "Pendiente",
            'Vence': p['end_date'].strftime('%Y-%m-%d'),
            'Pagado': p['date_paid'].strftime('%Y-%m-%d') if p['date_paid'] else 'N/A'
        }
        for p in all_payments
    ])
    
    # Sort by loan ID and payment ID
    payments_df = payments_df.sort_values(['ID Préstamo', 'Pago #'])
    st.dataframe(payments_df, use_container_width=True)


def view_payments_by_month(all_payments):
    # Get all unique months from payment end dates
    all_months = set()
    for payment in all_payments:
        month_key = payment['end_date'].strftime('%Y-%m')
        all_months.add(month_key)
    
    if not all_months:
        st.info("No hay pagos disponibles.")
        return
    
    # Month selection
    sorted_months = sorted(list(all_months))
    selected_month = st.selectbox(
        "Selecciona un mes:",
        sorted_months,
        key="view_payments_month"
    )
    
    # Filter payments for selected month
    month_payments = [
        p for p in all_payments 
        if p['end_date'].strftime('%Y-%m') == selected_month
    ]
    
    if not month_payments:
        st.info(f"No hay pagos para el mes {selected_month}.")
        return
    
    # Create summary statistics for the month
    total_month_payments = len(month_payments)
    paid_month_payments = len([p for p in month_payments if p['status'] == PaymentStatus.PAID.value])
    pending_month_payments = total_month_payments - paid_month_payments
    
    add_n_line_jumps(1)
    st.subheader(f"Pagos del mes {selected_month}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pagos", total_month_payments)
    with col2:
        st.metric("Pagos Realizados", paid_month_payments)
    with col3:
        st.metric("Pagos Pendientes", pending_month_payments)
    
    # Sort payments by status (pending first) and then by end_date
    month_payments_sorted = sorted(
        month_payments, 
        key=lambda x: (
            0 if x['status'] == PaymentStatus.PENDING.value else 1,  # Pending first
            x['end_date']  # Then by end date
        )
    )
    
    # Display payments table
    payments_df = pd.DataFrame([
        {
            'ID Préstamo': p['loan_id'],
            'Código': p['loan_code'],
            'Cliente': p['borrower_name'],
            'Teléfono': p['borrower_phone'],
            'Vehículo': f"{p['car_info']}",
            'Pago #': p['payment_id'],
            'Monto': f"${p['amount']:.2f}",
            'Estado': "Pagado" if p['status'] == PaymentStatus.PAID.value else "Pendiente",
            'Vence': p['end_date'].strftime('%Y-%m-%d'),
            'Pagado': p['date_paid'].strftime('%Y-%m-%d') if p['date_paid'] else 'N/A'
        }
        for p in month_payments_sorted
    ])
    
    st.dataframe(payments_df, use_container_width=True)
    
    # Show action insights for pending payments
    pending_payments_for_month = [p for p in month_payments_sorted if p['status'] == PaymentStatus.PENDING.value]
    
    if pending_payments_for_month:
        add_n_line_jumps(1)
        st.subheader("📋 Acciones Sugeridas")
        st.write("**Pagos pendientes ordenados por proximidad de vencimiento:**")
        
        today = datetime.now().date()
        
        for i, payment in enumerate(pending_payments_for_month, 1):
            days_until_due = (payment['end_date'].date() - today).days
            
            if days_until_due < 0:
                status_icon = "🔴"
                status_text = f"VENCIDO hace {abs(days_until_due)} días"
            elif days_until_due == 0:
                status_icon = "🟠"
                status_text = "VENCE HOY"
            elif days_until_due <= 3:
                status_icon = "🟡"
                status_text = f"Vence en {days_until_due} días"
            else:
                status_icon = "🟢"
                status_text = f"Vence en {days_until_due} días"
            
            st.write(f"{status_icon} **{i}.** {payment['borrower_name']} - ${payment['amount']:.2f} - {status_text}")
        
        # Action buttons
        add_n_line_jumps(1)
        st.subheader("🚀 Acciones Rápidas")
        col1, col2, col3, _ = st.columns([1, 1, 1, 1.5])
        
        atrasados = col1.button("📞 Llamar Clientes Atrasados", key="call_overdue")
        recordatorios = col2.button("📧 Enviar Recordatorios", key="send_reminders")
        reporte = col3.button("📊 Generar Reporte", key="generate_report")
        
        if atrasados:
            overdue_clients = [p for p in pending_payments_for_month if (p['end_date'].date() - today).days < 0]
            if overdue_clients:
                st.success(f"📞 Lista de llamadas generada para {len(overdue_clients)} clientes vencidos")
                for client in overdue_clients:
                    st.write(f"• {client['loan_code']} - {client['borrower_name']} - {client['borrower_phone']}")
            else:
                st.info("No hay clientes vencidos este mes")
        
        if recordatorios:
                due_soon = [p for p in pending_payments_for_month if (p['end_date'].date() - today).days <= 3]
                if due_soon:
                    st.success(f"📧 Recordatorios enviados a {len(due_soon)} clientes")
                    for client in due_soon:
                        st.write(f"• {client['loan_code']} - {client['borrower_name']} - {client['borrower_phone']}")
                else:
                    st.info("No hay pagos próximos a vencer")
        
        if reporte:
                st.success("📊 Reporte generado exitosamente")
                st.write(f"**Resumen del mes {selected_month}:**")
                st.write(f"• Total de pagos a recibir este mes: {total_month_payments}")
                st.write(f"• Pagos realizados este mes: {paid_month_payments}")
                st.write(f"• Pagos pendientes este mes: {pending_month_payments}")
                st.write(f"• Clientes atrasados este mes: {len([p for p in pending_payments_for_month if (p['end_date'].date() - today).days < 0])}")
    else:
        st.success("🎉 ¡Excelente! Todos los pagos de este mes han sido realizados.")
