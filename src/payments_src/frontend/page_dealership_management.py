import uuid

import streamlit as st

from payments_src.db.csv_db.db_constants import CSVTable
from payments_src.db.csv_db.db_operations import (
    read_dealership_table,
    append_dealership_table,
    write_dealership_table,
    edit_dealership_table_record,
)
from payments_src.domain.dealerships import Dealership, DealershipFactory
from payments_src.frontend.enums.enums_dealership_management import DealershipManagementActions
from payments_src.shared.pydantic_validation_utils import get_field_input_widget_dealership
from payments_src.frontend.utils import add_n_line_jumps


def dealership_management_page():
    st.title("Gestión de Automotoras")

    short_col, _ = st.columns([1, 4])

    selected_action = short_col.selectbox(
        "Selecciona una acción",
        DealershipManagementActions.list(),
        index=0,
        key="dealership_management_action"
    )

    if selected_action == DealershipManagementActions.ADD_DEALERSHIP.value:
        dealership_fields = Dealership.get_fields_and_types()

        with st.form("add_dealership_form", clear_on_submit=True, enter_to_submit=False):
            st.write("Formulario para agregar una automotora")

            dealership_form_data = {}

            for field_name, field_info in dealership_fields.items():
                if field_name.startswith('_'):
                    continue

                field_value = get_field_input_widget_dealership(
                    field_name=field_name,
                    field_info=field_info,
                    key=f"form_{field_name}"
                )

                dealership_form_data[field_name] = field_value

                st.caption(f"Tipo de dato: {field_info.annotation.__name__}")

            submitted = st.form_submit_button("Agregar Automotora")

            if submitted:
                
                dealership_table = read_dealership_table()

                if len(dealership_table) == 0:
                    next_id = 1
                else:
                    next_id = dealership_table['dealership_id'].astype(int).max() + 1
                dealership_form_data["dealership_id"] = next_id

                new_dealership = DealershipFactory.create_dealership(**dealership_form_data)

                if new_dealership.dealership_code in dealership_table['dealership_code'].values:
                    raise ValueError("El codigo de la automotora ya existe. Intenta con otro código.")

                dealership_table = append_dealership_table(dealership_table, new_dealership)
                write_dealership_table(dealership_table, overwrite=True)


    elif selected_action == DealershipManagementActions.VIEW_DEALERSHIP.value:
        dealership_table = read_dealership_table()

        st.dataframe(dealership_table)

    elif selected_action == DealershipManagementActions.EDIT_DEALERSHIP.value:
        dealership_table = read_dealership_table()
        
        if len(dealership_table) == 0:
            st.warning("No hay automotoras registradas para editar.")
        else:
            dealership_table_copy = dealership_table.copy()
            dealership_table_copy["display_name"] = dealership_table_copy["dealership_id"].astype(str) + " - " + dealership_table_copy["name"]

            options = dealership_table_copy['display_name'].tolist()

            short_col, _ = st.columns([1, 4])

            dealership_display_name = short_col.selectbox("Selecciona una automotora", options, index=0, key="dealership_display_name")

            dealership_dict = dealership_table[dealership_table_copy['display_name'] == dealership_display_name].iloc[0].to_dict()
            dealership = Dealership(**dealership_dict)

            st.subheader(f"Editando: {dealership.name}")

            current_values_col, edit_values_col = st.columns(2)

            with current_values_col:
                st.write("**Valores Actuales:**")
                dealership_fields = Dealership.get_fields_and_types()
                
                for field_name, field_info in dealership_fields.items():
                    if field_name.startswith('_'):
                        continue
                    
                    current_value = getattr(dealership, field_name)
                    st.text_input(
                        f"{field_name} (actual)",
                        value=str(current_value),
                        disabled=True,
                        key=f"current_{field_name}"
                    )

            with edit_values_col:
                st.write("**Nuevos Valores:**")
                
                with st.form("edit_dealership_form", clear_on_submit=False):
                    dealership_form_data = {}
                    
                    for field_name, field_info in dealership_fields.items():
                        if field_name.startswith('_'):
                            continue
                        
                        current_value = getattr(dealership, field_name)
                        
                        field_value = get_field_input_widget_dealership(
                            field_name=field_name,
                            field_info=field_info,
                            key=f"edit_{field_name}"
                        )
                        
                        # If no new value provided, use current value
                        if field_value is None or field_value == "":
                            field_value = current_value
                        
                        dealership_form_data[field_name] = field_value
                        st.caption(f"Tipo de dato: {field_info.annotation.__name__}")

                    submitted = st.form_submit_button("Guardar Cambios")

                    if submitted:
                        try:
                            dealership_form_data["dealership_id"] = dealership.dealership_id
                            
                            dealership_table_check = read_dealership_table()
                            other_dealerships = dealership_table_check[dealership_table_check['dealership_id'] != dealership.dealership_id]
                            
                            if dealership_form_data["dealership_code"] in other_dealerships['dealership_code'].values:
                                raise ValueError("El código de la automotora ya existe. Intenta con otro código.")
                            else:
                                updated_dealership = Dealership(**dealership_form_data)
                                
                                dealership_table = read_dealership_table()
                                dealership_table = edit_dealership_table_record(dealership_table, updated_dealership)
                                write_dealership_table(dealership_table, overwrite=True)
                                
                                st.success(f"Automotora '{updated_dealership.name}' actualizada exitosamente!")
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"Error al actualizar la automotora: {str(e)}")

        
    elif selected_action == DealershipManagementActions.DELETE_DEALERSHIP.value:
        dealership_table = read_dealership_table()

        if len(dealership_table) == 0:
            st.warning("No hay automotoras registradas para eliminar.")
        else:
            dealership_table_copy = dealership_table.copy()
            dealership_table_copy["display_name"] = dealership_table_copy["dealership_id"].astype(str) + " - " + dealership_table_copy["name"]

            options = dealership_table_copy['display_name'].tolist()

            short_col, _ = st.columns([1, 4])

            dealership_display_name = short_col.selectbox("Selecciona una automotora", options, index=0, key="dealership_display_name")

            add_n_line_jumps(1)
            delete_dealership = st.button("Eliminar Automotora", key="delete_dealership_button")

            if delete_dealership:
                dealership_table_to_write = dealership_table[dealership_table_copy['display_name'] != dealership_display_name]
                write_dealership_table(dealership_table_to_write, overwrite=True)
                st.success(f"Automotora '{dealership_display_name}' eliminada exitosamente!")
                st.rerun()

