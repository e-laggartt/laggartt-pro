import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_radiator_data
from utils.calculator import parse_quantity
from utils.session_manager import initialize_session_state

def create_radiator_matrix():
    """Создает матрицу радиаторов с вводом данных"""
    
    # Инициализация состояния сессии
    initialize_session_state()
    
    st.title("🔧 Подбор радиаторов METEOR")
    st.markdown("---")
    
    # Боковая панель управления
    with st.sidebar:
        st.header("⚙️ Параметры подбора")
        
        # Выбор подключения
        connection = st.radio(
            "**Вид подключения:**",
            ["VK-правое", "VK-левое", "K-боковое"],
            key="connection"
        )
        
        # Адаптивный выбор типа радиатора
        if connection == "VK-левое":
            radiator_types = ["10", "11", "30", "33"]
        else:
            radiator_types = ["10", "11", "20", "21", "22", "30", "33"]
            
        radiator_type = st.radio(
            "**Тип радиатора:**",
            radiator_types,
            key="radiator_type"
        )
        
        # Выбор кронштейнов
        bracket_type = st.radio(
            "**Тип крепления:**",
            ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"],
            key="bracket_type"
        )
        
        st.markdown("---")
        st.subheader("💰 Скидки")
        
        col1, col2 = st.columns(2)
        with col1:
            radiator_discount = st.number_input(
                "Радиаторы, %:",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key="radiator_discount"
            )
        
        with col2:
            bracket_discount = st.number_input(
                "Кронштейны, %:",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key="bracket_discount"
            )
        
        st.markdown("---")
        st.subheader("🛠️ Инструменты")
        
        if st.button("📋 Предпросмотр спецификации", use_container_width=True):
            st.session_state.show_preview = True
            
        if st.button("🗑️ Сброс всех данных", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('matrix_'):
                    del st.session_state[key]
            st.rerun()
    
    # Основная область - матрица радиаторов
    st.header(f"Матрица радиаторов: {connection} {radiator_type}")
    
    # Загрузка данных радиаторов
    sheet_name = f"{connection} {radiator_type}"
    radiator_data = load_radiator_data(sheet_name)
    
    if radiator_data is None:
        st.error(f"Данные для '{sheet_name}' не найдены")
        return
    
    # Создание матрицы
    create_matrix_interface(radiator_data, sheet_name)
    
    # Предпросмотр спецификации
    if st.session_state.get('show_preview', False):
        show_specification_preview(radiator_data, sheet_name)

def create_matrix_interface(radiator_data, sheet_name):
    """Создает интерфейс матрицы радиаторов"""
    
    # Определяем размеры
    heights = [300, 400, 500, 600, 900]
    lengths = list(range(400, 2100, 100))  # 400-2000 с шагом 100
    
    # Создаем контейнер для матрицы
    matrix_container = st.container()
    
    with matrix_container:
        # Заголовок матрицы
        cols = st.columns([2] + [1] * len(heights))
        
        with cols[0]:
            st.markdown("**Длина →<br>Высота ↓**", unsafe_allow_html=True)
        
        for i, height in enumerate(heights):
            with cols[i + 1]:
                st.markdown(f"**{height}**")
        
        # Строки матрицы
        for length in lengths:
            cols = st.columns([2] + [1] * len(heights))
            
            with cols[0]:
                st.markdown(f"**{length}**")
            
            for i, height in enumerate(heights):
                with cols[i + 1]:
                    create_matrix_cell(length, height, radiator_data, sheet_name)

def create_matrix_cell(length, height, radiator_data, sheet_name):
    """Создает ячейку матрицы с вводом данных"""
    
    # Находим соответствующий радиатор
    pattern = f"/{height}/{length}"
    matching_radiators = radiator_data[
        radiator_data['Наименование'].str.contains(pattern, na=False)
    ]
    
    if matching_radiators.empty:
        st.markdown("—")
        return
    
    radiator = matching_radiators.iloc[0]
    articul = str(radiator['Артикул']).strip()
    cell_key = f"matrix_{sheet_name}_{articul}"
    
    # Инициализация значения ячейки
    if cell_key not in st.session_state:
        st.session_state[cell_key] = ""
    
    # Создаем поле ввода
    current_value = st.session_state[cell_key]
    
    # Определяем цвет фона в зависимости от заполненности
    if current_value and parse_quantity(current_value) > 0:
        background_color = "#e6f3ff"  # Голубой для заполненных
    else:
        background_color = "#ffffff"  # Белый для пустых
    
    # Поле ввода с кастомным стилем
    new_value = st.text_input(
        "",
        value=current_value,
        key=f"input_{cell_key}",
        label_visibility="collapsed",
        placeholder="0",
        help=f"""
        Артикул: {articul}
        Мощность: {radiator.get('Мощность, Вт', 'N/A')} Вт
        Вес: {radiator.get('Вес, кг', 'N/A')} кг
        Объем: {radiator.get('Объем, м3', 'N/A')} м³
        Цена: {radiator.get('Цена, руб', 'N/A')} руб
        """
    )
    
    # Валидация ввода
    if new_value != current_value:
        if validate_matrix_input(new_value):
            st.session_state[cell_key] = new_value
            st.rerun()
        else:
            st.session_state[cell_key] = current_value
            st.error("Разрешены только цифры и знак '+'")

def validate_matrix_input(value):
    """Валидация вводимых данных в матрице"""
    if value == "":
        return True
    
    # Разрешаем только цифры и знак +
    if all(char.isdigit() or char == '+' for char in value):
        # Проверяем, что знак + не в начале/конце и не дублируется
        cleaned = value.strip('+')
        if '++' not in cleaned:
            return True
    
    return False

def show_specification_preview(radiator_data, sheet_name):
    """Показывает предпросмотр спецификации"""
    
    st.markdown("---")
    st.header("📋 Предпросмотр спецификации")
    
    # Собираем данные из матрицы
    spec_data = collect_specification_data(radiator_data, sheet_name)
    
    if spec_data.empty:
        st.warning("Нет данных для формирования спецификации")
        return
    
    # Отображаем таблицу спецификации
    display_specification_table(spec_data)
    
    # Кнопки экспорта
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Экспорт в Excel", use_container_width=True):
            export_to_excel(spec_data)
    
    with col2:
        if st.button("📄 Экспорт в CSV", use_container_width=True):
            export_to_csv(spec_data)
    
    with col3:
        if st.button("📋 Перейти к спецификации", use_container_width=True):
            st.switch_page("pages/02_📋_Спецификация.py")

def collect_specification_data(radiator_data, sheet_name):
    """Собирает данные для спецификации из заполненной матрицы"""
    
    spec_rows = []
    
    for _, radiator in radiator_data.iterrows():
        articul = str(radiator['Артикул']).strip()
        cell_key = f"matrix_{sheet_name}_{articul}"
        
        quantity = parse_quantity(st.session_state.get(cell_key, ""))
        
        if quantity > 0:
            price = float(radiator.get('Цена, руб', 0))
            discount = st.session_state.get('radiator_discount', 0.0)
            discounted_price = price * (1 - discount / 100)
            total = discounted_price * quantity
            
            spec_rows.append({
                'Артикул': articul,
                'Наименование': radiator['Наименование'],
                'Мощность, Вт': radiator.get('Мощность, Вт', 0),
                'Цена, руб (с НДС)': price,
                'Скидка, %': discount,
                'Цена со скидкой, руб (с НДС)': discounted_price,
                'Кол-во': quantity,
                'Сумма, руб (с НДС)': total
            })
    
    return pd.DataFrame(spec_rows)

def display_specification_table(spec_data):
    """Отображает таблицу спецификации"""
    
    if not spec_data.empty:
        # Добавляем нумерацию
        spec_data_display = spec_data.copy()
        spec_data_display.insert(0, '№', range(1, len(spec_data) + 1))
        
        # Форматируем числовые колонки
        format_dict = {
            'Цена, руб (с НДС)': '{:,.2f}',
            'Цена со скидкой, руб (с НДС)': '{:,.2f}', 
            'Сумма, руб (с НДС)': '{:,.2f}'
        }
        
        st.dataframe(
            spec_data_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Итоги
        total_sum = spec_data['Сумма, руб (с НДС)'].sum()
        total_qty = spec_data['Кол-во'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Общее количество", f"{total_qty} шт.")
        with col2:
            st.metric("Общая стоимость", f"{total_sum:,.2f} руб")

def export_to_excel(spec_data):
    """Экспорт в Excel"""
    # Здесь будет логика экспорта в Excel
    st.success("Функция экспорта в Excel будет реализована")

def export_to_csv(spec_data):
    """Экспорт в CSV"""
    # Здесь будет логика экспорта в CSV
    st.success("Функция экспорта в CSV будет реализована")

if __name__ == "__main__":
    create_radiator_matrix()