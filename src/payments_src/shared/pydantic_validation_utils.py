import streamlit as st
from typing import Any

from payments_src.domain.borrower_enums import PotentialBorrowerStatus


def get_field_input_widget_potential_borrower(field_name: str, field_info: Any, key: str):
    """Create appropriate input widget based on field type"""
    field_type = field_info.annotation
    
    # Handle different field types
    if field_type == str:
        return st.text_input(field_name, key=key)
    elif field_type == int:
        return st.number_input(field_name, step=1, key=key)
    elif field_type == float:
        return st.number_input(field_name, step=0.01, key=key)
    elif field_type == bool:
        return st.checkbox(field_name, key=key)
    elif field_type == PotentialBorrowerStatus:
        # For enum fields, create a selectbox
        options = [status.value for status in PotentialBorrowerStatus]
        return st.selectbox(field_name, options, key=key)
    else:
        # Fallback to text input for unknown types
        return st.text_input(field_name, key=key)
    

def get_field_input_widget_car(field_name: str, field_info: Any, key: str):
    """Create appropriate input widget based on field type"""
    field_type = field_info.annotation
    
    # Handle different field types
    if field_type == str:
        return st.text_input(field_name, key=key)
    elif field_type == int:
        return st.number_input(field_name, step=1, key=key)