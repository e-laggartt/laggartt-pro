# Главная.py
import streamlit as st
import pandas as pd
from utils.calculator import parse_quantity, calculate_brackets
from utils.session_manager import initialize_session_state

def main():
    # Инициализация состояния
    initialize_session_state()
    
    st.title("🏠 Матрица радиаторов")
    
    if 'sheets' not in st.session_state or not st.session_state.sheets:
        st.error("❌ Данные не загружены. Проверьте наличие файла data/Матрица.xlsx")
        
        # Кнопка для принудительной перезагрузки данных
        if st.button("🔄 Перезагрузить данные"):
            from utils.data_loader import load_radiator_data
            st.session_state.sheets = load_radiator_data()
            st.rerun()
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
        st.session_state.connection = connection
        
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
        st.session_state.radiator_type = radiator_type
        
        # Выбор кронштейнов
        st.subheader("Крепление")
        bracket_type = st.radio(
            "Тип крепления:",
            ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"],
            index=0,
            key="bracket_radio"
        )
        st.session_state.bracket_type = bracket_type
        
        # Скидки
        st.subheader("💰 Скидки")
        col1, col2 = st.columns(2)
        with col1:
            rad_discount = st.number_input(
                "Радиаторы, %",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.discounts["radiators"],
                step=1.0,
                key="rad_discount_input"
            )
        with col2:
            br_discount = st.number_input(
                "Кронштейны, %",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.discounts["brackets"],
                step=1.0,
                key="br_discount_input"
            )
        
        st.session_state.discounts = {
            "radiators": rad_discount,
            "brackets": br_discount
        }
        
        # Дополнительные настройки
        st.subheader("⚙️ Настройки")
        show_tooltips = st.checkbox(
            "Показывать подсказки", 
            value=st.session_state.show_tooltips,
            key="tooltips_checkbox"
        )
        st.session_state.show_tooltips = show_tooltips
        
        # Быстрые действия
        st.markdown("---")
        st.subheader("🚀 Быстрые действия")
        
        if st.button("🗑️ Очистить матрицу", type="secondary"):
            st.session_state.entry_values = {}
            st.rerun()
            
        if st.button("📋 Перейти к спецификации", type="primary"):
            st.switch_page("pages/02_📋_Спецификация.py")
    
    # Основная область - матрица радиаторов
    st.header(f"📊 Матрица: {connection} {radiator_type}")
    
    sheet_name = f"{connection} {radiator_type}"
    if sheet_name not in sheets:
        st.error(f"❌ Лист '{sheet_name}' не найден в данных")
        st.info("Доступные листы:")
        for available_sheet in sheets.keys():
            st.write(f"- {available_sheet}")
        return
    
    df = sheets[sheet_name]
    lengths = list(range(400, 2100, 100))  # 400-2000 с шагом 100
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
    total_filled = 0
    total_quantity = 0
    
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
                    
                    # Поле ввода с валидацией
                    new_val = st.text_input(
                        "",
                        value=current_val,
                        key=f"matrix_{l}_{h}_{i}_{j}",
                        label_visibility="collapsed",
                        placeholder="0"
                    )
                    
                    # Валидация ввода
                    if new_val and not all(c in '0123456789+' for c in new_val):
                        st.error("Только цифры и +")
                        new_val = current_val
                    
                    if new_val != current_val:
                        st.session_state.entry_values[key] = new_val
                        quantity = parse_quantity(new_val)
                        if quantity > 0:
                            total_filled += 1
                            total_quantity += quantity
                    
                    # Подсказка при наведении
                    if st.session_state.show_tooltips and product is not None:
                        power = product.get('Мощность, Вт', 'N/A')
                        weight = product.get('Вес, кг', 'N/A')
                        volume = product.get('Объем, м3', 'N/A')
                        price = product.get('Цена, руб', 'N/A')
                        
                        tooltip_text = f"""
                        **{product.get('Наименование', 'N/A')}**
                        
                        🔹 Артикул: {art}
                        🔹 Мощность: {power} Вт
                        🔹 Вес: {weight} кг
                        🔹 Объем: {volume} м³
                        🔹 Цена: {price} ₽
                        """
                        
                        if new_val and parse_quantity(new_val) > 0:
                            qty = parse_quantity(new_val)
                            tooltip_text += f"\n🔹 Выбрано: {qty} шт"
                        
                        st.markdown(f"<span title='{tooltip_text}'>ℹ️</span>", unsafe_allow_html=True)
                else:
                    st.markdown("—")
    
    # Статистика и навигация
    if total_filled > 0:
        st.success(f"✅ Заполнено ячеек: {total_filled} | Общее количество: {total_quantity} шт")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Просмотреть спецификацию", type="primary", use_container_width=True):
                st.switch_page("pages/02_📋_Спецификация.py")
        with col2:
            if st.button("🔄 Обновить статистику", use_container_width=True):
                st.rerun()
    else:
        st.info("💡 Заполните ячейки матрицы для формирования спецификации")

if __name__ == "__main__":
    main()