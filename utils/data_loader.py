import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_radiator_data(sheet_name):
    """Загружает данные радиаторов из Excel файла"""
    
    try:
        file_path = "data/Матрица.xlsx"
        
        # Если файла нет, создаем тестовые данные
        if not os.path.exists(file_path):
            st.warning("Файл данных не найден. Создаю тестовые данные...")
            create_test_data()
        
        # Читаем все листы для проверки
        excel_file = pd.ExcelFile(file_path)
        
        if sheet_name not in excel_file.sheet_names:
            st.error(f"Лист '{sheet_name}' не найден в файле. Доступные листы: {excel_file.sheet_names}")
            return create_fallback_data(sheet_name)
        
        # Загружаем данные
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Предобработка данных
        data['Артикул'] = data['Артикул'].astype(str).str.strip()
        data['Наименование'] = data['Наименование'].astype(str)
        
        # Заполняем числовые колонки
        numeric_columns = ['Мощность, Вт', 'Вес, кг', 'Объем, м3', 'Цена, руб']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        return data
        
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {str(e)}")
        return create_fallback_data(sheet_name)

def create_test_data():
    """Создает тестовые данные если файл не найден"""
    try:
        import numpy as np
        
        heights = [300, 400, 500, 600, 900]
        lengths = list(range(400, 2100, 100))
        
        combinations = [
            ("VK-правое", "10"), ("VK-правое", "11"), ("VK-правое", "20"),
            ("VK-правое", "21"), ("VK-правое", "22"), ("VK-правое", "30"),
            ("VK-правое", "33"), ("VK-левое", "10"), ("VK-левое", "11"),
            ("VK-левое", "30"), ("VK-левое", "33"), ("K-боковое", "10"),
            ("K-боковое", "11"), ("K-боковое", "20"), ("K-боковое", "21"),
            ("K-боковое", "22"), ("K-боковое", "30"), ("K-боковое", "33"),
        ]
        
        with pd.ExcelWriter('data/Матрица.xlsx', engine='openpyxl') as writer:
            for connection, rad_type in combinations:
                sheet_data = []
                
                for height in heights:
                    for length in lengths:
                        articul = f"R{rad_type}{height}{length}"
                        name = f"Радиатор METEOR {connection} тип {rad_type}/{height}мм/{length}мм"
                        power = max(100, length * 0.5 + height * 0.3)
                        weight = max(5, length * 0.01 + height * 0.005)
                        volume = max(0.001, length * height * 0.000001)
                        price = max(1000, length * 2 + height * 1)
                        
                        sheet_data.append({
                            'Артикул': articul,
                            'Наименование': name,
                            'Мощность, Вт': round(power, 1),
                            'Вес, кг': round(weight, 2),
                            'Объем, м3': round(volume, 4),
                            'Цена, руб': round(price, 2)
                        })
                
                df = pd.DataFrame(sheet_data)
                sheet_name = f"{connection} {rad_type}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        st.success("Тестовые данные созданы успешно!")
        return True
        
    except Exception as e:
        st.error(f"Ошибка создания тестовых данных: {e}")
        return False

def create_fallback_data(sheet_name):
    """Создает fallback данные если загрузка не удалась"""
    try:
        heights = [300, 400, 500, 600, 900]
        lengths = list(range(400, 2100, 100))
        
        sheet_data = []
        for height in heights:
            for length in lengths:
                articul = f"FALLBACK{height}{length}"
                name = f"Радиатор {sheet_name}/{height}мм/{length}мм"
                
                sheet_data.append({
                    'Артикул': articul,
                    'Наименование': name,
                    'Мощность, Вт': 500,
                    'Вес, кг': 10.0,
                    'Объем, м3': 0.01,
                    'Цена, руб': 2000.0
                })
        
        return pd.DataFrame(sheet_data)
        
    except Exception:
        return pd.DataFrame()