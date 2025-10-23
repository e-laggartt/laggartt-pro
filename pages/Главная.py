import streamlit as st
import pandas as pd
from utils.calculator import parse_quantity, calculate_brackets

def main():
    st.title("🏠 Матрица радиаторов")
    
    if 'sheets' not in st.session_state:
        st.error("Данные не загружены. Вернитесь на главную страницу.")
        return
    
    sheets = st.session_state.sheets
    
    # Боковая панель управления
    with st.sidebar:
        st.header("🔧 Параметры подбора")
        
        # Выбор подключения
        st.subheader("Подключение")
        connection = st.radio(
            "Вид подключения:",
            ["VK-правое", "VK-левое", "K-боковое"],
            index=0,
            key="connection_radio"
        )
        
        # Выбор типа радиатора
        st.subheader("Тип радиатора")
        if connection == "VK-левое":
            rad_types = ["10", "11", "30", "33"]
        else:
            rad_types = ["10", "11", "20", "21", "22", "30", "33"]
            
        radiator_type = st.radio(
            "Тип:",
            rad_types,
            index=0,
            key="radiator_radio"
        )
        
        # Выбор кронштейнов
        st.subheader("Крепление")
        bracket_type = st.radio(
            "Тип крепления:",
            ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"],
            index=0,
            key="bracket_radio"
        )
        
        # Скидки
        st.subheader("💰 Скидки")
        col1, col2 = st.columns(2)
        with col1:
            rad_discount = st.number_input(
                "Радиаторы, %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key="rad_discount_input"
            )
        with col2:
            br_discount = st.number_input(
                "Кронштейны, %",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key="br_discount_input"
            )
    
    # Основная область - матрица радиаторов
    st.header(f"📊 Матрица: {connection} {radiator_type}")
    
    sheet_name = f"{connection} {radiator_type}"
    if sheet_name not in sheets:
        st.error(f"Лист '{sheet_name}' не найден в данных")
        return
    
    df = sheets[sheet_name]
    lengths = list(range(400, 2100, 100))
    heights = [300, 400, 500, 600, 900]
    
    # Создание матрицы
    st.markdown("#### длина радиаторов, мм →")
    
    # Заголовки столбцов (высоты)
    cols = st.columns(len(heights) + 1)
    with cols[0]:
        st.markdown("**высота<br>радиаторов, мм**", unsafe_allow_html=True)
    
    for j, h in enumerate(heights):
        with cols[j + 1]:
            st.markdown(f"**{h}**")
    
    # Строки матрицы
    has_any_value = any(st.session_state.entry_values.values())
    
    for i, l in enumerate(lengths):
        cols = st.columns(len(heights) + 1)
        
        # Заголовок строки (длина)
        with cols[0]:
            st.markdown(f"**{l}**")
        
        # Ячейки матрицы
        for j, h in enumerate(heights):
            with cols[j + 1]:
                pattern = f"/{h}мм/{l}мм"
                match = df[df['Наименование'].str.contains(pattern, na=False)]
                
                if not match.empty:
                    product = match.iloc[0]
                    art = str(product['Артикул'])
                    key = (sheet_name, art)
                    
                    current_val = st.session_state.entry_values.get(key, "")
                    
                    # Поле ввода
                    new_val = st.text_input(
                        "",
                        value=current_val,
                        key=f"matrix_{i}_{j}",
                        label_visibility="collapsed",
                        placeholder="0"
                    )
                    
                    if new_val != current_val:
                        st.session_state.entry_values[key] = new_val
                        
                    # Подсказка при наведении
                    if st.session_state.get('show_tooltips', True) and new_val:
                        with st.expander("", expanded=False):
                            st.caption(f"🔹 Артикул: {art}")
                            st.caption(f"🔹 Мощность: {product.get('Мощность, Вт', 'N/A')} Вт")
                            st.caption(f"🔹 Вес: {product.get('Вес, кг', 'N/A')} кг")
    
    # Статистика
    total_entries = len([v for v in st.session_state.entry_values.values() if v])
    if total_entries > 0:
        st.success(f"✅ Заполнено ячеек: {total_entries}")
        
        if st.button("📋 Перейти к спецификации", type="primary"):
            st.switch_page("pages/02_📋_Спецификация.py")

if __name__ == "__main__":
    main()