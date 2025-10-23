import pandas as pd
import streamlit as st
from pathlib import Path

def validate_data(sheets, brackets_df):
    """Валидация загруженных данных"""
    errors = []
    
    # Проверка обязательных листов
    required_connections = ["VK-правое", "VK-левое", "K-боковое"]
    required_types = ["10", "11", "20", "21", "22", "30", "33"]
    
    for connection in required_connections:
        for rad_type in required_types:
            sheet_name = f"{connection} {rad_type}"
            if sheet_name not in sheets:
                # Пропускаем комбинации, которые не должны существовать
                if connection == "VK-левое" and rad_type in ["20", "21", "22"]:
                    continue
                elif sheet_name not in sheets:
                    errors.append(f"Отсутствует лист: {sheet_name}")
    
    # Проверка структуры данных
    for sheet_name, df in sheets.items():
        required_columns = ['Артикул', 'Наименование', 'Мощность, Вт', 'Вес, кг', 'Объем, м3', 'Цена, руб']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"В листе {sheet_name} отсутствуют колонки: {', '.join(missing_columns)}")
    
    return errors