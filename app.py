# app.py
import streamlit as st
import pandas as pd
from utils.data_loader import load_radiator_matrix
from utils.calculator import calculate_brackets, parse_quantity

# Настройка страницы
st.set_page_config(
    page_title="RadiaTool Pro v2.0",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Загрузка CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Инициализация состояния сессии
def initialize_session_state():
    if 'entry_values' not in st.session_state:
        st.session_state.entry_values = {}
    if 'connection' not in st.session_state:
        st.session_state.connection = "VK-правое"
    if 'radiator_type' not in st.session_state:
        st.session_state.radiator_type = "10"
    if 'bracket_type' not in st.session_state:
        st.session_state.bracket_type = "Настенные"
    if 'discounts' not in st.session_state:
        st.session_state.discounts = {"radiators": 0, "brackets": 0}
    if 'spec_data' not in st.session_state:
        st.session_state.spec_data = pd.DataFrame()

# Главная функция
def main():
    load_css()
    initialize_session_state()
    
    # Заголовок
    st.title("🔧 RadiaTool Pro v2.0")
    st.markdown("---")
    
    # Боковая панель
    with st.sidebar:
        st.image("assets/images/logo.png", width=200)  # Заглушка для лого
        st.header("🔧 ПАРАМЕТРЫ ПОДБОРА")
        
        # Выбор подключения
        connection = st.radio(
            "Подключение:",
            ["VK-правое", "VK-левое", "K-боковое"],
            index=0
        )
        st.session_state.connection = connection
        
        # Выбор типа радиатора
        if connection.startswith("VK"):
            rad_types = ["10", "11", "30", "33"]
        else:
            rad_types = ["10", "11", "20", "21", "22", "30", "33"]
            
        radiator_type = st.selectbox("Тип радиатора:", rad_types)
        st.session_state.radiator_type = radiator_type
        
        # Выбор крепления
        bracket_type = st.radio(
            "Крепление:",
            ["Настенные", "Напольные", "Без"]
        )
        st.session_state.bracket_type = bracket_type
        
        # Скидки
        st.subheader("Скидки:")
        rad_discount = st.number_input("Радиаторы (%):", 0, 100, 0)
        br_discount = st.number_input("Кронштейны (%):", 0, 100, 0)
        st.session_state.discounts = {
            "radiators": rad_discount,
            "brackets": br_discount
        }
        
        st.markdown("---")
        st.header("📁 ИНСТРУМЕНТЫ")
        
        if st.button("📤 Импорт данных"):
            st.switch_page("pages/03_📊_Импорт_данных.py")
            
        if st.button("📥 Экспорт спецификации"):
            st.switch_page("pages/02_📋_Спецификация.py")
            
        if st.button("📋 Предпросмотр"):
            st.switch_page("pages/02_📋_Спецификация.py")
            
        if st.button("🗑️ Сброс", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.header("ℹ️ ИНФОРМАЦИЯ")
        
        if st.button("📖 Инструкция"):
            st.switch_page("pages/04_ℹ️_Информация.py")
            
        if st.button("💰 Прайс-лист"):
            st.info("Функция в разработке")
            
        if st.button("📄 Сертификаты"):
            st.info("Функция в разработке")
            
        if st.button("🛠️ Поддержка"):
            st.info("mt@laggartt.ru")

    # Основная область - матрица радиаторов
    st.header(f"Матрица радиаторов: {connection} {radiator_type}")
    
    # Загрузка матрицы
    matrix_data = load_radiator_matrix(connection, radiator_type)
    
    # Создание матрицы ввода
    heights = [300, 400, 500, 600, 900]
    lengths = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
    
    # Сетка для матрицы
    cols = st.columns(len(lengths) + 1)
    
    # Заголовки столбцов (длины)
    with cols[0]:
        st.write("**Высота** → **Длина**")
    for i, length in enumerate(lengths):
        with cols[i + 1]:
            st.write(f"**{length}**")
    
    # Строки матрицы
    for height in heights:
        cols = st.columns(len(lengths) + 1)
        
        with cols[0]:
            st.write(f"**{height}**")
            
        for i, length in enumerate(lengths):
            with cols[i + 1]:
                key = f"{height}_{length}"
                value = st.session_state.entry_values.get(key, "")
                
                # Поле ввода с валидацией
                new_value = st.text_input(
                    "",
                    value=value,
                    key=key,
                    label_visibility="collapsed",
                    placeholder="0"
                )
                
                # Валидация ввода
                if new_value:
                    if all(c in '0123456789+' for c in new_value):
                        st.session_state.entry_values[key] = new_value
                    else:
                        st.error("Только цифры и +")
                        st.session_state.entry_values[key] = ""

if __name__ == "__main__":
    main()