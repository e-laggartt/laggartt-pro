# utils/data_loader.py
import pandas as pd
import streamlit as st
import openpyxl

@st.cache_data
def load_radiator_data():
    """
    Загрузка данных радиаторов из Excel файла
    """
    try:
        # Загрузка основного файла матрицы
        file_path = "data/Матрица.xlsx"
        
        # Чтение всех листов
        sheets_dict = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        
        # Предобработка данных
        processed_sheets = {}
        for sheet_name, df in sheets_dict.items():
            # Приведение артикулов к строковому типу
            if 'Артикул' in df.columns:
                df['Артикул'] = df['Артикул'].astype(str)
            
            # Заполнение пропущенных числовых значений
            numeric_columns = ['Мощность, Вт', 'Вес, кг', 'Объем, м3', 'Цена, руб']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            processed_sheets[sheet_name] = df
        
        return processed_sheets
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")
        return {}

@st.cache_data
def load_brackets_data():
    """
    Загрузка базы кронштейнов
    """
    try:
        file_path = "data/Кронштейны.xlsx"
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Предобработка
        if 'Артикул' in df.columns:
            df['Артикул'] = df['Артикул'].astype(str)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки кронштейнов: {e}")
        return pd.DataFrame()

def get_radiator_by_size(df, height, length):
    """
    Поиск радиатора по высоте и длине в DataFrame
    """
    pattern = f"/{height}мм/{length}мм"
    matches = df[df['Наименование'].str.contains(pattern, na=False)]
    
    if not matches.empty:
        return matches.iloc[0]
    return None