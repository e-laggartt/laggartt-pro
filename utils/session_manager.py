# utils/session_manager.py
import streamlit as st
import pandas as pd
import json
import os

def initialize_session_state():
    """
    Инициализация состояния сессии согласно ТЗ
    """
    # Загрузка данных
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
        'mappings': load_mappings(),
        'current_page': 'Главная'
    }
    
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_mappings():
    """
    Загрузка сохраненных соответствий
    """
    try:
        if os.path.exists("data/mappings.json"):
            with open("data/mappings.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Ошибка загрузки соответствий: {e}")
    return {}

def save_mappings():
    """
    Сохранение соответствий в файл
    """
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/mappings.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.get('mappings', {}), f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения соответствий: {e}")

def clear_session():
    """
    Очистка сессии
    """
    keys_to_keep = ['sheets', 'mappings']  # Сохраняем загруженные данные
    new_state = {k: v for k, v in st.session_state.items() if k in keys_to_keep}
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    for key, value in new_state.items():
        st.session_state[key] = value
    
    # Повторная инициализация
    initialize_session_state()

def get_specification_data():
    """
    Формирование данных для спецификации на основе заполненной матрицы
    """
    from utils.calculator import parse_quantity, calculate_brackets
    
    spec_rows = []
    
    # Обработка радиаторов
    for key, value in st.session_state.entry_values.items():
        if value and parse_quantity(value) > 0:
            sheet_name, art = key
            quantity = parse_quantity(value)
            
            # Поиск данных о продукте
            if sheet_name in st.session_state.sheets:
                df = st.session_state.sheets[sheet_name]
                product_match = df[df['Артикул'] == art]
                
                if not product_match.empty:
                    product = product_match.iloc[0]
                    
                    # Извлечение параметров из наименования
                    name = product.get('Наименование', '')
                    height, length = extract_dimensions_from_name(name)
                    
                    price = product.get('Цена, руб', 0)
                    power = product.get('Мощность, Вт', 0)
                    weight = product.get('Вес, кг', 0)
                    volume = product.get('Объем, м3', 0)
                    
                    spec_rows.append({
                        "Артикул": art,
                        "Наименование": name,
                        "Количество": quantity,
                        "Цена": price,
                        "Сумма": quantity * price,
                        "Мощность, Вт": power,
                        "Вес, кг": weight,
                        "Объем, м3": volume,
                        "Тип": "Радиатор"
                    })
    
    # Добавление кронштейнов
    if st.session_state.bracket_type != "Без кронштейнов":
        bracket_rows = generate_brackets_specification()
        spec_rows.extend(bracket_rows)
    
    return pd.DataFrame(spec_rows)

def extract_dimensions_from_name(name):
    """
    Извлечение высоты и длины из наименования
    """
    import re
    height, length = 0, 0
    
    # Поиск паттерна /500мм/1000мм
    pattern = r'/(\d+)мм/(\d+)мм'
    match = re.search(pattern, str(name))
    if match:
        height = int(match.group(1))
        length = int(match.group(2))
    
    return height, length

def generate_brackets_specification():
    """
    Генерация спецификации кронштейнов
    """
    from utils.calculator import parse_quantity, calculate_brackets
    
    bracket_rows = []
    brackets_data = load_brackets_data()
    
    # Расчет кронштейнов для каждого радиатора
    for key, value in st.session_state.entry_values.items():
        if value and parse_quantity(value) > 0:
            sheet_name, art = key
            quantity = parse_quantity(value)
            
            # Поиск данных о продукте для получения размеров
            if sheet_name in st.session_state.sheets:
                df = st.session_state.sheets[sheet_name]
                product_match = df[df['Артикул'] == art]
                
                if not product_match.empty:
                    product = product_match.iloc[0]
                    name = product.get('Наименование', '')
                    height, length = extract_dimensions_from_name(name)
                    
                    # Расчет кронштейнов
                    brackets = calculate_brackets(
                        st.session_state.radiator_type,
                        length, height,
                        st.session_state.bracket_type,
                        quantity
                    )
                    
                    # Добавление кронштейнов в спецификацию
                    for bracket_art, bracket_qty in brackets:
                        # Поиск данных о кронштейне
                        if not brackets_data.empty and 'Артикул' in brackets_data.columns:
                            bracket_match = brackets_data[brackets_data['Артикул'] == bracket_art]
                            if not bracket_match.empty:
                                bracket_product = bracket_match.iloc[0]
                                bracket_name = bracket_product.get('Наименование', f'Кронштейн {bracket_art}')
                                bracket_price = bracket_product.get('Цена, руб', 0)
                            else:
                                bracket_name = f'Кронштейн {bracket_art}'
                                bracket_price = 0
                        else:
                            bracket_name = f'Кронштейн {bracket_art}'
                            bracket_price = 0
                        
                        bracket_rows.append({
                            "Артикул": bracket_art,
                            "Наименование": bracket_name,
                            "Количество": bracket_qty,
                            "Цена": bracket_price,
                            "Сумма": bracket_qty * bracket_price,
                            "Мощность, Вт": 0,
                            "Вес, кг": 0,
                            "Объем, м3": 0,
                            "Тип": "Кронштейн"
                        })
    
    return bracket_rows

def load_brackets_data():
    """
    Загрузка данных кронштейнов
    """
    try:
        from utils.data_loader import load_brackets_data as load_brackets
        return load_brackets()
    except:
        return pd.DataFrame()