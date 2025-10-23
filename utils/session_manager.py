# utils/session_manager.py
import streamlit as st
import pandas as pd
import json

def initialize_session_state():
    """
    Инициализация состояния сессии согласно ТЗ
    """
    if 'sheets' not in st.session_state:
        from utils.data_loader import load_radiator_data
        st.session_state.sheets = load_radiator_data()
    
    # Основные параметры из ТЗ
    default_state = {
        'entry_values': {},
        'connection': "VK-правое",
        'radiator_type': "10", 
        'bracket_type': "Настенные кронштейны",
        'discounts': {"radiators": 0, "brackets": 0},
        'spec_data': pd.DataFrame(),
        'imported_data': pd.DataFrame(),
        'show_tooltips': True,
        'mappings': load_mappings()
    }
    
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_mappings():
    """
    Загрузка сохраненных соответствий
    """
    try:
        with open("data/mappings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_mappings():
    """
    Сохранение соответствий в файл
    """
    try:
        with open("data/mappings.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.get('mappings', {}), f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения соответствий: {e}")

def clear_matrix():
    """
    Очистка матрицы
    """
    st.session_state.entry_values = {}
    st.rerun()