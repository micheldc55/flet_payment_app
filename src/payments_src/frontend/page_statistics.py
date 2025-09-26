import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from payments_src.db.csv_db.db_operations import read_and_expand_loans_table, read_loan_table
from payments_src.domain.loans_enums import LoanStatus
from payments_src.domain.payment_enums import PaymentStatus
from payments_src.domain.loans import Loan
from payments_src.frontend.utils import add_n_line_jumps


def statistics_page():
    st.title("📊 Estadísticas de Préstamos")
    
    # Get all loans data
    all_loans_df = read_and_expand_loans_table(LoanStatus.POTENTIAL)  # This gets all loans regardless of status
    approved_loans_df = read_and_expand_loans_table(LoanStatus.APPROVED)
    
    if approved_loans_df.empty:
        st.info("No hay datos de préstamos disponibles.")
        return
    
    # Create tabs for different statistics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Resumen General", "💰 Dinero Pendiente", "📅 Análisis Mensual", "💼 Proyecciones de Inversión"])
    
    with tab1:
        general_statistics_tab(all_loans_df, approved_loans_df)
    
    with tab2:
        pending_money_tab(approved_loans_df)
    
    with tab3:
        monthly_analysis_tab(approved_loans_df)
    
    with tab4:
        investment_projections_tab(approved_loans_df)


def general_statistics_tab(all_loans_df, approved_loans_df):
    st.header("📈 Resumen General")
    
    # Calculate acceptance rate
    total_decided_loans = len(all_loans_df[all_loans_df['status'] != LoanStatus.POTENTIAL.value])
    approved_loans_count = len(approved_loans_df)
    rejected_loans_count = len(all_loans_df[all_loans_df['status'] == LoanStatus.REJECTED.value])
    
    if total_decided_loans > 0:
        acceptance_rate = (approved_loans_count / total_decided_loans) * 100
    else:
        acceptance_rate = 0
    
    # Calculate total investment
    total_investment = sum(loan['payment_list'].dinero_total_prestado for _, loan in approved_loans_df.iterrows())
    
    # Calculate total expected revenue
    total_expected_revenue = 0
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        total_expected_revenue += sum(payment.amount for payment in loan.payment_list.payments.values())
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tasa de Aceptación",
            f"{acceptance_rate:.1f}%",
            f"{approved_loans_count}/{total_decided_loans}"
        )
    
    with col2:
        st.metric(
            "Préstamos Aprobados",
            approved_loans_count,
            f"Rechazados: {rejected_loans_count}"
        )
    
    with col3:
        st.metric(
            "Inversión Total",
            f"${total_investment:,.2f}",
            "En préstamos activos"
        )
    
    with col4:
        st.metric(
            "Ingresos Esperados",
            f"${total_expected_revenue:,.2f}",
            f"Ganancia: ${total_expected_revenue - total_investment:,.2f}"
        )
    
    # Status distribution chart
    st.subheader("Distribución de Estados de Préstamos")
    
    status_counts = all_loans_df['status'].value_counts()
    status_labels = {
        LoanStatus.POTENTIAL.value: "Potenciales",
        LoanStatus.APPROVED.value: "Aprobados", 
        LoanStatus.REJECTED.value: "Rechazados"
    }
    
    fig = px.pie(
        values=status_counts.values,
        names=[status_labels.get(status, status) for status in status_counts.index],
        title="Distribución de Préstamos por Estado"
    )
    st.plotly_chart(fig, use_container_width=True)


def pending_money_tab(approved_loans_df):
    st.header("💰 Dinero Pendiente de Cobro")
    
    # Overall pending money
    total_pending = 0
    total_paid = 0
    
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            if payment.status == PaymentStatus.PENDING.value:
                total_pending += payment.amount
            else:
                total_paid += payment.amount
    
    # Display overall metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Pendiente", f"${total_pending:,.2f}")
    
    with col2:
        st.metric("Total Cobrado", f"${total_paid:,.2f}")
    
    with col3:
        total_expected = total_pending + total_paid
        collection_rate = (total_paid / total_expected * 100) if total_expected > 0 else 0
        st.metric("Tasa de Cobro", f"{collection_rate:.1f}%")
    
    # Monthly breakdown
    st.subheader("Análisis por Mes")
    
    # Get month selection
    all_months = set()
    monthly_data = defaultdict(lambda: {'pending': 0, 'paid': 0, 'total': 0})
    
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            month_key = payment.end_date.strftime('%Y-%m')
            all_months.add(month_key)
            monthly_data[month_key]['total'] += payment.amount
            
            if payment.status == PaymentStatus.PENDING.value:
                monthly_data[month_key]['pending'] += payment.amount
            else:
                monthly_data[month_key]['paid'] += payment.amount
    
    if all_months:
        sorted_months = sorted(list(all_months))
        selected_month = st.selectbox(
            "Selecciona un mes para ver detalles:",
            sorted_months,
            key="pending_money_month"
        )
        
        month_data = monthly_data[selected_month]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Pendiente {selected_month}", f"${month_data['pending']:,.2f}")
        with col2:
            st.metric(f"Cobrado {selected_month}", f"${month_data['paid']:,.2f}")
        with col3:
            collection_rate_month = (month_data['paid'] / month_data['total'] * 100) if month_data['total'] > 0 else 0
            st.metric(f"Tasa Cobro {selected_month}", f"{collection_rate_month:.1f}%")
        
        # Monthly trend chart
        st.subheader("Tendencia Mensual de Cobros")
        
        monthly_df = pd.DataFrame([
            {
                'Mes': month,
                'Pendiente': data['pending'],
                'Cobrado': data['paid'],
                'Total': data['total']
            }
            for month, data in monthly_data.items()
        ]).sort_values('Mes')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_df['Mes'],
            y=monthly_df['Pendiente'],
            mode='lines+markers',
            name='Pendiente',
            line=dict(color='red')
        ))
        fig.add_trace(go.Scatter(
            x=monthly_df['Mes'],
            y=monthly_df['Cobrado'],
            mode='lines+markers',
            name='Cobrado',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title="Evolución de Pagos Pendientes vs Cobrados",
            xaxis_title="Mes",
            yaxis_title="Monto ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def monthly_analysis_tab(approved_loans_df):
    st.header("📅 Análisis de Pagos Mensuales")
    
    # Time window selection
    col1, col2 = st.columns(2)
    
    with col1:
        months_ahead = st.number_input(
            "Número de meses a analizar:",
            min_value=1,
            max_value=24,
            value=12,
            key="months_ahead"
        )
    
    with col2:
        start_date = st.date_input(
            "Fecha de inicio:",
            value=date.today(),
            key="analysis_start_date"
        )
    
    # Calculate end date
    end_date = start_date + relativedelta(months=months_ahead)
    
    st.write(f"**Período de análisis:** {start_date.strftime('%Y-%m')} a {end_date.strftime('%Y-%m')}")
    
    # Collect monthly payment data
    monthly_payments = defaultdict(lambda: {'count': 0, 'total_amount': 0, 'pending_count': 0, 'pending_amount': 0})
    
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            payment_month = payment.end_date.strftime('%Y-%m')
            
            # Check if payment is within our analysis window
            if start_date <= payment.end_date.date() <= end_date:
                monthly_payments[payment_month]['count'] += 1
                monthly_payments[payment_month]['total_amount'] += payment.amount
                
                if payment.status == PaymentStatus.PENDING.value:
                    monthly_payments[payment_month]['pending_count'] += 1
                    monthly_payments[payment_month]['pending_amount'] += payment.amount
    
    if monthly_payments:
        # Create DataFrame for analysis
        analysis_df = pd.DataFrame([
            {
                'Mes': month,
                'Total Pagos': data['count'],
                'Monto Total': data['total_amount'],
                'Pagos Pendientes': data['pending_count'],
                'Monto Pendiente': data['pending_amount'],
                'Pagos Realizados': data['count'] - data['pending_count'],
                'Monto Cobrado': data['total_amount'] - data['pending_amount']
            }
            for month, data in monthly_payments.items()
        ]).sort_values('Mes')
        
        # Display summary metrics
        total_payments_in_period = analysis_df['Total Pagos'].sum()
        total_amount_in_period = analysis_df['Monto Total'].sum()
        total_pending_in_period = analysis_df['Monto Pendiente'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pagos", total_payments_in_period)
        with col2:
            st.metric("Monto Total", f"${total_amount_in_period:,.2f}")
        with col3:
            st.metric("Pendiente", f"${total_pending_in_period:,.2f}")
        with col4:
            collection_rate_period = ((total_amount_in_period - total_pending_in_period) / total_amount_in_period * 100) if total_amount_in_period > 0 else 0
            st.metric("Tasa Cobro", f"{collection_rate_period:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Número de Pagos por Mes")
            fig1 = px.bar(
                analysis_df,
                x='Mes',
                y='Total Pagos',
                title="Cantidad de Pagos por Mes"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("Monto de Pagos por Mes")
            fig2 = px.bar(
                analysis_df,
                x='Mes',
                y='Monto Total',
                title="Monto Total de Pagos por Mes"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed table
        st.subheader("Detalle Mensual")
        st.dataframe(analysis_df, use_container_width=True)
        
        # Balance analysis
        st.subheader("Análisis de Balance")
        
        avg_monthly_payments = analysis_df['Total Pagos'].mean()
        avg_monthly_amount = analysis_df['Monto Total'].mean()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Promedio Pagos/Mes", f"{avg_monthly_payments:.1f}")
        with col2:
            st.metric("Promedio Monto/Mes", f"${avg_monthly_amount:,.2f}")
        
        # Identify months with unusual activity
        std_payments = analysis_df['Total Pagos'].std()
        std_amount = analysis_df['Monto Total'].std()
        
        unusual_months = analysis_df[
            (analysis_df['Total Pagos'] > avg_monthly_payments + std_payments) |
            (analysis_df['Total Pagos'] < avg_monthly_payments - std_payments) |
            (analysis_df['Monto Total'] > avg_monthly_amount + std_amount) |
            (analysis_df['Monto Total'] < avg_monthly_amount - std_amount)
        ]
        
        if not unusual_months.empty:
            st.subheader("⚠️ Meses con Actividad Inusual")
            st.dataframe(unusual_months[['Mes', 'Total Pagos', 'Monto Total']], use_container_width=True)
        else:
            st.success("✅ No se detectaron meses con actividad inusual en el período analizado.")
    
    else:
        st.info("No hay pagos en el período seleccionado.")


def investment_projections_tab(approved_loans_df):
    st.header("💼 Proyecciones de Inversión")
    
    # Current investment calculation
    total_investment = sum(loan['payment_list'].dinero_total_prestado for _, loan in approved_loans_df.iterrows())
    
    # Projection date selection
    col1, col2 = st.columns(2)
    
    with col1:
        projection_date = st.date_input(
            "Fecha de proyección:",
            value=date.today() + relativedelta(months=6),
            key="projection_date"
        )
    
    with col2:
        st.metric("Inversión Actual", f"${total_investment:,.2f}")
    
    # Calculate projected money by projection date
    projected_money = 0
    total_expected_revenue = 0
    
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            total_expected_revenue += payment.amount
            
            # If payment is due before or on projection date, add to projected money
            if payment.end_date.date() <= projection_date:
                if payment.status == PaymentStatus.PAID.value:
                    projected_money += payment.amount
                else:
                    # Assume pending payments will be paid by projection date
                    projected_money += payment.amount
    
    # Calculate revenue
    projected_revenue = projected_money - total_investment
    
    # Display projections
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Dinero Proyectado",
            f"${projected_money:,.2f}",
            f"Para {projection_date.strftime('%Y-%m-%d')}"
        )
    
    with col2:
        st.metric(
            "Ingresos Proyectados",
            f"${projected_revenue:,.2f}",
            f"ROI: {(projected_revenue/total_investment*100):.1f}%" if total_investment > 0 else "ROI: 0%"
        )
    
    with col3:
        remaining_revenue = total_expected_revenue - projected_money
        st.metric(
            "Ingresos Futuros",
            f"${remaining_revenue:,.2f}",
            f"Después de {projection_date.strftime('%Y-%m')}"
        )
    
    with col4:
        collection_rate_projection = (projected_money / total_expected_revenue * 100) if total_expected_revenue > 0 else 0
        st.metric(
            "Tasa Cobro Proyectada",
            f"{collection_rate_projection:.1f}%",
            f"Hasta {projection_date.strftime('%Y-%m')}"
        )
    
    # Monthly projection chart
    st.subheader("Proyección Mensual de Ingresos")
    
    # Calculate monthly projections
    monthly_projections = defaultdict(float)
    current_date = date.today()
    
    while current_date <= projection_date:
        month_key = current_date.strftime('%Y-%m')
        monthly_projections[month_key] = 0
        current_date += relativedelta(months=1)
    
    # Fill in actual and projected payments
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            payment_month = payment.end_date.strftime('%Y-%m')
            if payment_month in monthly_projections:
                monthly_projections[payment_month] += payment.amount
    
    # Create projection chart
    projection_df = pd.DataFrame([
        {'Mes': month, 'Ingresos': amount}
        for month, amount in monthly_projections.items()
    ]).sort_values('Mes')
    
    fig = px.bar(
        projection_df,
        x='Mes',
        y='Ingresos',
        title=f"Proyección de Ingresos hasta {projection_date.strftime('%Y-%m')}"
    )
    
    # Add cumulative line
    projection_df['Cumulative'] = projection_df['Ingresos'].cumsum()
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=projection_df['Mes'],
        y=projection_df['Ingresos'],
        name='Ingresos Mensuales',
        marker_color='lightblue'
    ))
    fig2.add_trace(go.Scatter(
        x=projection_df['Mes'],
        y=projection_df['Cumulative'],
        mode='lines+markers',
        name='Ingresos Acumulados',
        yaxis='y2',
        line=dict(color='red', width=3)
    ))
    
    fig2.update_layout(
        title=f"Proyección de Ingresos Acumulados hasta {projection_date.strftime('%Y-%m')}",
        xaxis_title="Mes",
        yaxis_title="Ingresos Mensuales ($)",
        yaxis2=dict(title="Ingresos Acumulados ($)", overlaying="y", side="right"),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Risk analysis
    st.subheader("Análisis de Riesgo")
    
    # Calculate overdue payments
    today = date.today()
    overdue_payments = 0
    overdue_amount = 0
    
    for _, loan_row in approved_loans_df.iterrows():
        loan = Loan(**loan_row.to_dict())
        for payment in loan.payment_list.payments.values():
            if payment.status == PaymentStatus.PENDING.value and payment.end_date.date() < today:
                overdue_payments += 1
                overdue_amount += payment.amount
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Pagos Vencidos", overdue_payments)
    
    with col2:
        st.metric("Monto Vencido", f"${overdue_amount:,.2f}")
    
    if overdue_amount > 0:
        risk_percentage = (overdue_amount / total_expected_revenue * 100) if total_expected_revenue > 0 else 0
        st.warning(f"⚠️ {risk_percentage:.1f}% de los ingresos esperados están en riesgo por pagos vencidos.")
    else:
        st.success("✅ No hay pagos vencidos. Excelente gestión de cobros.")
