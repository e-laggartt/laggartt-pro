import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# === КОНФИГУРАЦИЯ СТРАНИЦЫ ===
st.set_page_config(
    page_title="RadiaTool Pro v2.0",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === ЗАГРУЗКА ДАННЫХ ===
@st.cache_data
def load_data():
    """Загрузка данных из Excel файлов"""
    try:
        matrix_path = Path("data/Матрица.xlsx")
        brackets_path = Path("data/Кронштейны.xlsx")
        
        if not matrix_path.exists():
            st.error("❌ Файл 'Матрица.xlsx' не найден в папке data/")
            st.stop()
        if not brackets_path.exists():
            st.error("❌ Файл 'Кронштейны.xlsx' не найден в папке data/")
            st.stop()
            
        # Загрузка матрицы радиаторов
        sheets = pd.read_excel(matrix_path, sheet_name=None, engine="openpyxl")
        
        # Загрузка кронштейнов
        brackets_df = pd.read_excel(brackets_path, engine="openpyxl")
        brackets_df['Артикул'] = brackets_df['Артикул'].astype(str).str.strip()
        
        # Предобработка данных матрицы
        for name, df in sheets.items():
            if name != "Кронштейны":
                df['Артикул'] = df['Артикул'].astype(str).str.strip()
                df['Вес, кг'] = pd.to_numeric(df['Вес, кг'], errors='coerce').fillna(0)
                df['Объем, м3'] = pd.to_numeric(df['Объем, м3'], errors='coerce').fillna(0)
                df['Мощность, Вт'] = pd.to_numeric(df['Мощность, Вт'], errors='coerce').fillna(0)
                
        return sheets, brackets_df
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {str(e)}")
        st.stop()

# === ИНИЦИАЛИЗАЦИЯ СЕССИИ ===
def init_session_state():
    """Инициализация состояния сессии"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.entry_values = {}
        st.session_state.connection = "VK-правое"
        st.session_state.radiator_type = "10"
        st.session_state.bracket_type = "Настенные кронштейны"
        st.session_state.radiator_discount = 0.0
        st.session_state.bracket_discount = 0.0
        st.session_state.spec_data = pd.DataFrame()
        st.session_state.show_tooltips = True

# === ГЛАВНЫЙ ИНТЕРФЕЙС ===
def main():
    init_session_state()
    
    # Загрузка данных
    sheets, brackets_df = load_data()
    st.session_state.sheets = sheets
    st.session_state.brackets_df = brackets_df
    
    # Заголовок приложения
    st.title("🔧 RadiaTool Pro v2.0")
    st.markdown("---")
    
    # Информация о загруженных данных
    with st.sidebar:
        st.success(f"✅ Загружено листов: {len(sheets)}")
        st.success(f"✅ Кронштейнов: {len(brackets_df)}")
        
        st.markdown("---")
        st.markdown("### 🛠️ Быстрые действия")
        
        if st.button("🔄 Сброс данных", use_container_width=True):
            st.session_state.entry_values = {}
            st.session_state.spec_data = pd.DataFrame()
            st.rerun()
            
        if st.button("📋 Предпросмотр", use_container_width=True):
            if len(st.session_state.entry_values) > 0:
                st.switch_page("pages/02_📋_Спецификация.py")
            else:
                st.warning("Сначала заполните матрицу радиаторов")
    
    # Основной контент
    st.info("🚀 **Добро пожаловать в RadiaTool Pro!** Выберите раздел в боковом меню для начала работы.")

if __name__ == "__main__":
    main()