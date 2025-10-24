# pages/01_🏠_Главная.py
import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import re

# === Загрузка данных ===
@st.cache_data
def load_data():
    matrix_path = Path("data/Матрица.xlsx")
    brackets_path = Path("data/Кронштейны.xlsx")
    if not matrix_path.exists():
        st.error("❌ Файл 'Матрица.xlsx' не найден")
        st.stop()
    if not brackets_path.exists():
        st.error("❌ Файл 'Кронштейны.xlsx' не найден")
        st.stop()
    
    sheets = pd.read_excel(matrix_path, sheet_name=None, engine="openpyxl")
    brackets_df = pd.read_excel(brackets_path, engine="openpyxl")
    
    # Обработка кронштейнов
    if "Кронштейны" in sheets:
        brackets_df = sheets["Кронштейны"].copy()
        del sheets["Кронштейны"]
    
    brackets_df['Артикул'] = brackets_df['Артикул'].astype(str).str.strip()
    
    # Обработка листов с радиаторами
    for name, df in sheets.items():
        df['Артикул'] = df['Артикул'].astype(str).str.strip()
        df['Вес, кг'] = pd.to_numeric(df['Вес, кг'], errors='coerce').fillna(0)
        df['Объем, м3'] = pd.to_numeric(df['Объем, м3'], errors='coerce').fillna(0)
        df['Мощность, Вт'] = df.get('Мощность, Вт', '')
    
    return sheets, brackets_df

sheets, brackets_df = load_data()

# === Инициализация состояния ===
if "connection" not in st.session_state:
    st.session_state.connection = "VK-правое"
if "radiator_type" not in st.session_state:
    st.session_state.radiator_type = "10"
if "bracket_type" not in st.session_state:
    st.session_state.bracket_type = "Настенные кронштейны"
if "radiator_discount" not in st.session_state:
    st.session_state.radiator_discount = 0.0
if "bracket_discount" not in st.session_state:
    st.session_state.bracket_discount = 0.0
if "entry_values" not in st.session_state:
    st.session_state.entry_values = {}
if "show_tooltips" not in st.session_state:
    st.session_state.show_tooltips = False
if "last_validation_error" not in st.session_state:
    st.session_state.last_validation_error = None
if "show_selected_items" not in st.session_state:
    st.session_state.show_selected_items = False
    

# === Функции из tkinter приложения ===
def validate_input(val):
    """Проверяет вводимые данные в ячейках. Разрешает цифры и знаки +"""
    if val == "":  # Разрешаем пустую строку
        return True
    # Разрешаем только цифры и знак +
    pattern = r'^[\d+]+$'
    return bool(re.match(pattern, val))

def parse_quantity(value):
    """
    Преобразует введенное значение в количество радиаторов.
    Обрабатывает целые числа, числа с плавающей точкой и комбинации с плюсами.
    """
    try:
        if isinstance(value, str) and value.strip() in ["Кол-во", "№"]:
            return 0
            
        if not value:
            return 0
        
        if isinstance(value, (int, float)):
            return int(round(float(value)))
    
        value = str(value).strip()
        
        # Удаляем лишние знаки '+' в начале и конце
        while value.startswith('+'):
            value = value[1:]
        while value.endswith('+'):
            value = value[:-1]
        
        if not value:
            return 0
        
        parts = value.split('+')
        total = 0
        for part in parts:
            part = part.strip()
            if part:
                total += int(round(float(part)))
                
        return total
    except Exception as e:
        print(f"Ошибка преобразования количества: {str(e)}")
        return 0

def get_product_info(sheet_name, art):
    """Получает информацию о продукте по артикулу"""
    if sheet_name in sheets:
        data = sheets[sheet_name]
        product = data[data['Артикул'] == art]
        if not product.empty:
            return product.iloc[0]
    return None

def has_any_value():
    """Проверяет, есть ли хотя бы одно значение во всех матрицах"""
    return any(val and val != "0" for val in st.session_state.entry_values.values())

def get_cell_color(has_values, cell_value):
    """Определяет цвет ячейки"""
    if cell_value and cell_value != "0":
        return "#e6f3ff"  # Голубой для заполненных ячеек
    elif has_values:
        return "#e6f3ff"  # Голубой для всех ячеек, если есть заполненные
    else:
        return "white"    # Белый если нет заполненных ячеек

def get_selected_items():
    """Получает список выбранных позиций"""
    selected_items = []
    for key, value in st.session_state.entry_values.items():
        if value and value != "0":
            # Ключ имеет формат: "VK-правое_10_7724651420"
            # Или: "input_0_0_VK-правое_10_7724651420" для полей ввода
            parts = key.split('_')
            
            # Если ключ начинается с "input", пропускаем первые 3 части
            if key.startswith('input_'):
                if len(parts) >= 6:
                    # Собираем sheet_name из оставшихся частей
                    sheet_parts = parts[3:-1]  # Все части кроме последней (артикул)
                    art = parts[-1]
                    sheet_name = ' '.join(sheet_parts)
                else:
                    continue
            else:
                # Старый формат ключа
                if len(parts) >= 3:
                    sheet_name = f"{parts[0]} {parts[1]}"
                    art = parts[2]
                else:
                    continue
            
            product = get_product_info(sheet_name, art)
            if product is not None:
                qty = parse_quantity(value)
                selected_items.append({
                    'Артикул': art,
                    'Наименование': product['Наименование'],
                    'Количество': qty,
                    'Вес, кг': product['Вес, кг'],
                    'Лист': sheet_name
                })
    return selected_items

def get_brackets_for_radiator(radiator, bracket_type):
    """Подбирает кронштейны для радиатора в зависимости от типа крепления"""
    if bracket_type == "Без кронштейнов":
        return []
    
    # Получаем вес радиатора
    weight = radiator['Вес, кг']
    
    # Определяем тип кронштейна для поиска
    if bracket_type == "Настенные кронштейны":
        search_pattern = "настен"
    else:  # Напольные кронштейны
        search_pattern = "напольн"
    
    # Ищем подходящие кронштейны
    suitable_brackets = []
    
    for _, bracket in brackets_df.iterrows():
        bracket_name = str(bracket['Наименование']).lower()
        
        # Проверяем соответствие типу
        if search_pattern in bracket_name:
            # Проверяем максимальную нагрузку кронштейна
            max_load = bracket.get('Макс_нагрузка', 0)
            try:
                max_load = float(max_load)
                if max_load >= weight:
                    suitable_brackets.append({
                        'Артикул': bracket['Артикул'],
                        'Наименование': bracket['Наименование'],
                        'Макс_нагрузка': max_load,
                        'Количество': radiator['Количество']  # Столько же сколько радиаторов
                    })
            except (ValueError, TypeError):
                continue
    
    return suitable_brackets

# === Компактный CSS с улучшениями ===
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .stRadio [data-testid="stMarkdownContainer"] {
        font-size: 14px;
        margin-bottom: 0;
    }
    
    .stHorizontalBlock {
        gap: 0.1rem;
    }
    
    div[data-testid="column"] {
        padding: 0px;
        margin: 0px;
    }
    
    h3 {
        margin-bottom: 0.5rem !important;
    }
    
    /* Улучшенные стили для матрицы */
    .matrix-header {
        font-weight: bold;
        text-align: center;
        font-size: 12px;
        padding: 2px !important;
        background-color: #f8f9fa;
        margin: 0px;
    }
    
    .matrix-corner {
        background-color: #f0f0f0;
    }
    
    /* Стили для текстовых полей */
    .stTextInput input {
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        height: 35px !important;
        padding: 0px 2px !important;
        margin: 0px !important;
    }
    
    /* Стиль для невалидного ввода */
    .invalid-input {
        border: 2px solid #ff4b4b !important;
        background-color: #ffe6e6 !important;
    }
    
    /* Скрываем лейблы */
    .hidden-label label {
        display: none;
    }
    
    /* Вертикальное расположение радиокнопок креплений */
    .vertical-radio .stRadio [role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    /* Стили для таблицы выбранных позиций */
    .selected-items-table {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    /* Уменьшаем отступы между колонками */
    [data-testid="column"] {
        gap: 0px;
    }
    
    /* Компактные отступы для матрицы */
    .compact-matrix {
        gap: 0px;
        margin: 0px;
        padding: 0px;
    }
    
    /* Уменьшаем отступы в ячейках матрицы */
    .matrix-cell {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Уменьшаем отступы между строками матрицы */
    .row {
        margin: 0px !important;
        padding: 0px !important;
        gap: 0px !important;
    }
    
    /* Уменьшаем вертикальные отступы */
    .element-container {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Компактные стили для всей матрицы */
    .matrix-container {
        margin: 0px !important;
        padding: 0px !important;
        gap: 0px !important;
    }
    
    /* Убираем лишние отступы вокруг текстовых полей */
    .stTextInput {
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Компактные заголовки */
    .compact-header {
        margin: 0px !important;
        padding: 2px !important;
    }
    
    /* СУПЕР КОМПАКТНЫЕ СТИЛИ ДЛЯ МАТРИЦЫ */
    /* Уменьшаем расстояние между колонками матрицы до минимума */
    [data-testid="column"] {
        gap: 1px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Минимальные отступы для всех элементов матрицы */
    .matrix-row {
        margin: 0px !important;
        padding: 0px !important;
        gap: 1px !important;
    }
    
    /* Ультра компактные поля ввода */
    .stTextInput {
        margin: 0px !important;
        padding: 0px !important;
        min-height: 0px !important;
    }
    
    .stTextInput input {
        height: 32px !important;
        padding: 0px 1px !important;
        margin: 0px !important;
        border-radius: 2px !important;
        border: 1px solid #ccc !important;
    }
    
    /* Уменьшаем отступы между строками матрицы */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
        gap: 1px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Компактные заголовки матрицы */
    .matrix-header-cell {
        padding: 1px 2px !important;
        margin: 0px !important;
        font-size: 11px !important;
        min-height: 20px !important;
    }
    
    /* Уменьшаем высоту строк матрицы */
    .matrix-input-row {
        min-height: 35px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# === Параметры подбора ===
st.markdown("### Матрица радиаторов")

# Подключение и тип радиатора
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Вид подключения**")
    connection_options = ["VK-правое", "VK-левое", "K-боковое"]
    connection = st.radio(
        "вид_подключения",
        connection_options,
        index=connection_options.index(st.session_state.connection),
        label_visibility="collapsed"
    )
    st.session_state.connection = connection

with col2:
    st.markdown("**Тип радиатора**")
    # Определяем доступные типы в зависимости от подключения
    if connection == "VK-левое":
        types = ["10", "11", "30", "33"]
    else:
        types = ["10", "11", "20", "21", "22", "30", "33"]
    
    if st.session_state.radiator_type not in types:
        st.session_state.radiator_type = types[0]
    
    rad_type = st.radio(
        "тип_радиатора",
        types,
        index=types.index(st.session_state.radiator_type),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.radiator_type = rad_type

# === Матрица радиаторов ===
sheet_name = f"{st.session_state.connection} {st.session_state.radiator_type}"

if sheet_name not in sheets:
    st.error(f"Лист '{sheet_name}' не найден")
else:
    data = sheets[sheet_name]
    lengths = list(range(400, 2100, 100))
    heights = [300, 400, 500, 600, 900]
    
    # Проверяем, есть ли заполненные ячейки для подсветки
    has_values = has_any_value()
    
    # Создаем матрицу как в tkinter версии
    st.markdown("---")
    
    # Создаем контейнер для заголовков высот
    height_cols = st.columns(len(heights) + 1)
    
    # Пустая ячейка в углу
    with height_cols[0]:
        st.markdown("")  # Пустое место
    
    # Подпись "Высота радиаторов, мм" над заголовками высот
    for j in range(len(heights) + 1):
        with height_cols[j]:
            if j == 0:
                # Первая колонка - подпись "Длина"
                st.markdown("<div style='text-align: center; font-weight: bold; margin: 0; padding: 0;'></div>", unsafe_allow_html=True)
            else:
                # Остальные колонки - высоты
                st.markdown(f"<div style='text-align: center; font-weight: bold; margin: 0; padding: 0;'>{heights[j-1]}</div>", unsafe_allow_html=True)
    
    # Тело матрицы - длины и ячейки ввода
    for i, length in enumerate(lengths):
        cols = st.columns(len(heights) + 1)
        
        # Заголовок строки - длина (без звездочек)
        with cols[0]:
            st.markdown(f"<div class='matrix-header' style='margin: 0; padding: 0;'>{length}</div>", unsafe_allow_html=True)
        
        # Ячейки ввода
        for j, height in enumerate(heights):
            pattern = f"/{height}/{length}"
            match = data[data['Наименование'].str.contains(pattern, na=False)]
            
            if not match.empty:
                product = match.iloc[0]
                art = str(product['Артикул']).strip()
                # Создаем простой ключ для хранения значения
                simple_key = f"{sheet_name.replace(' ', '_')}_{art}"
                current_value = st.session_state.entry_values.get(simple_key, "")
                
                # Убираем нули из отображения
                display_value = current_value if current_value != "0" else ""
                
                with cols[j + 1]:
                    # Создаем уникальный ключ для каждого поля ввода
                    input_key = f"input_{i}_{j}_{simple_key}"
                    
                    # Определяем цвет фона
                    cell_color = get_cell_color(has_values, current_value)
                    
                    # Создаем поле ввода с кастомным стилем
                    new_value = st.text_input(
                        f"Ячейка {length}x{height}",
                        value=display_value,
                        key=input_key,
                        label_visibility="collapsed",
                        placeholder=""
                    )
                    
                    # Валидация ввода при изменении
                    if new_value != display_value:
                        if validate_input(new_value):
                            # Сохраняем валидное значение по простому ключу
                            st.session_state.entry_values[simple_key] = new_value
                            st.session_state.last_validation_error = None
                            st.rerun()  # Перезагружаем для обновления цвета
                        else:
                            # Сохраняем ошибку и восстанавливаем предыдущее значение
                            st.session_state.last_validation_error = f"Неверный ввод: '{new_value}'. Можно вводить только цифры и знак +"
                            # Восстанавливаем предыдущее значение
                            st.session_state.entry_values[simple_key] = current_value
                            st.rerun()
                    
                    # Применяем стили через CSS классы
                    st.markdown(f"""
                    <style>
                    [data-testid="stTextInput"] [value="{new_value}"] {{
                        background-color: {cell_color} !important;
                        text-align: center !important;
                        font-size: 14px !important;
                        font-weight: 500 !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)

# === Показываем ошибки валидации ===
if st.session_state.last_validation_error:
    st.error(st.session_state.last_validation_error)
    # Очищаем ошибку после показа
    st.session_state.last_validation_error = None

# === Дополнительные параметры ===
st.markdown("---")

# Крепления и скидки в компактном виде
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("**Тип крепления**")
    bracket_options = ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"]
    
    # Добавляем CSS класс для вертикального расположения
    st.markdown('<div class="vertical-radio">', unsafe_allow_html=True)
    bracket = st.radio(
        "тип_крепления",
        bracket_options,
        index=bracket_options.index(st.session_state.bracket_type),
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.bracket_type = bracket

with col2:
    st.markdown("**Скидки**")
    disc_col1, disc_col2 = st.columns(2)
    
    with disc_col1:
        rad_disc = st.number_input(
            "на радиаторы, %",
            0.0, 100.0, st.session_state.radiator_discount, 1.0,
            key="rad_disc"
        )
        st.session_state.radiator_discount = rad_disc
    
    with disc_col2:
        br_disc = st.number_input(
            "на кронштейны, %",
            0.0, 100.0, st.session_state.bracket_discount, 1.0,
            key="br_disc"
        )
    st.session_state.bracket_discount = br_disc

# === Информация о заполненных ячейках ===
filled_cells = sum(1 for val in st.session_state.entry_values.values() if val and val != "0")
if filled_cells > 0:
    st.success(f"✅ Заполнено ячеек: {filled_cells}")
    
    # === ВЫБРАННЫЕ ПОЗИЦИИ (всегда показываем) ===
    selected_items = get_selected_items()
    if selected_items:
        st.markdown("### Выбранные позиции")
        
        # Создаем общий список всех позиций (радиаторы + кронштейны)
        all_items = []
        
        # Добавляем радиаторы
        for item in selected_items:
            all_items.append({
                'Артикул': item['Артикул'],
                'Наименование': item['Наименование'],
                'Количество': item['Количество'],
                'Тип': 'Радиатор'
            })
        
        # Добавляем кронштейны для каждого радиатора
        for radiator in selected_items:
            brackets = get_brackets_for_radiator(radiator, st.session_state.bracket_type)
            for bracket in brackets:
                all_items.append({
                    'Артикул': bracket['Артикул'],
                    'Наименование': bracket['Наименование'],
                    'Количество': bracket['Количество'],
                    'Тип': 'Кронштейн'
                })
        
        # Создаем DataFrame для отображения
        df = pd.DataFrame(all_items)
        
        # Группируем по артикулу и наименованию, суммируя количество
        grouped_df = df.groupby(['Артикул', 'Наименование', 'Тип']).agg({
            'Количество': 'sum'
        }).reset_index()
        
        # Отображаем таблицу
        st.dataframe(grouped_df, use_container_width=True)
        
        # Показываем итоговую информацию
        total_radiators = sum(item['Количество'] for item in selected_items)
        total_brackets = sum(bracket['Количество'] for radiator in selected_items 
                           for bracket in get_brackets_for_radiator(radiator, st.session_state.bracket_type))
        
        st.info(f"**Итого позиций:** {len(grouped_df)}, **Радиаторов:** {total_radiators}, **Кронштейнов:** {total_brackets}")

# === Кнопка сброса ===
if st.button("🔄 Сбросить все"):
    st.session_state.entry_values.clear()
    st.session_state.radiator_discount = 0.0
    st.session_state.bracket_discount = 0.0
    st.session_state.bracket_type = "Настенные кронштейны"
    st.session_state.last_validation_error = None
    st.session_state.show_selected_items = False
    st.rerun()

# === Отладочная информация (можно удалить) ===
with st.expander("Отладочная информация"):
    st.write("Заполненные значения:", {k: v for k, v in st.session_state.entry_values.items() if v and v != "0"})
    st.write("Все значения:", dict(st.session_state.entry_values))
    st.write("Есть ли заполненные ячейки:", has_any_value())
    st.write("Текущий лист:", sheet_name)
    st.write("Выбранные позиции:", get_selected_items())
    st.write("Ключи entry_values:", list(st.session_state.entry_values.keys()))