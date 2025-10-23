# app.py
import streamlit as st
import pandas as pd
from utils.data_loader import load_radiator_data  # ИСПРАВЛЕН ИМПОРТ
from utils.session_manager import initialize_session_state

# Настройка страницы
st.set_page_config(
    page_title="RadiaTool Pro v2.0",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Инициализация состояния
    initialize_session_state()
    
    # Заголовок
    st.title("🔧 RadiaTool Pro v2.0")
    st.markdown("---")
    
    # Информация о загруженных данных
    if 'sheets' in st.session_state and st.session_state.sheets:
        sheet_count = len(st.session_state.sheets)
        st.success(f"✅ Загружено листов данных: {sheet_count}")
        
        # Показать доступные листы
        with st.expander("📋 Просмотреть доступные листы"):
            for sheet_name in st.session_state.sheets.keys():
                st.write(f"- {sheet_name}")
    else:
        st.warning("⚠️ Данные не загружены. Используются демо-данные.")
    
    # Навигация по страницам
    st.header("🚀 Навигация")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Матрица радиаторов", use_container_width=True):
            st.switch_page("pages/Главная.py")
    
    with col2:
        if st.button("📋 Спецификация", use_container_width=True):
            st.switch_page("pages/02_📋_Спецификация.py")
    
    with col3:
        if st.button("📊 Импорт данных", use_container_width=True):
            st.switch_page("pages/03_📊_Импорт_данных.py")
    
    with col4:
        if st.button("ℹ️ Информация", use_container_width=True):
            st.switch_page("pages/04_ℹ️_Информация.py")
    
    # Быстрый старт
    st.markdown("---")
    st.header("🎯 Быстрый старт")
    
    st.markdown("""
    1. **Перейдите в "🏠 Матрица радиаторов"** для заполнения данных
    2. **Выберите параметры** в боковой панели:
       - Тип подключения (VK-правое, VK-левое, K-боковое)
       - Тип радиатора (10, 11, 20, 21, 22, 30, 33)
       - Тип крепления
    3. **Заполните матрицу** - вводите количества в ячейки
    4. **Перейдите в "📋 Спецификация"** для просмотра и экспорта
    """)
    
    # Статус системы
    st.markdown("---")
    st.header("📊 Статус системы")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        entry_count = len(st.session_state.entry_values)
        filled_count = len([v for v in st.session_state.entry_values.values() if v])
        st.metric("Заполнено ячеек", f"{filled_count}/{entry_count}")
    
    with col2:
        spec_count = len(st.session_state.spec_data) if hasattr(st.session_state.spec_data, '__len__') else 0
        st.metric("Позиций в спецификации", spec_count)
    
    with col3:
        st.metric("Версия", "2.0")

if __name__ == "__main__":
    main()