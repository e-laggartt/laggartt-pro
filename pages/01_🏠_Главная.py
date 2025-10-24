# pages/01_🏠_Главная.py
import streamlit as st
from pathlib import Path
import pandas as pd

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
    brackets_df['Артикул'] = brackets_df['Артикул'].astype(str).str.strip()
    for name, df in sheets.items():
        if name != "Кронштейны":
            df['Артикул'] = df['Артикул'].astype(str).str.strip()
            df['Вес, кг'] = pd.to_numeric(df['Вес, кг'], errors='coerce').fillna(0)
            df['Объем, м3'] = pd.to_numeric(df['Объем, м3'], errors='coerce').fillna(0)
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

# === Валидация ввода ===
def validate_input(val):
    if not val:
        return True
    return all(c.isdigit() or c == '+' for c in val)

# === Парсинг количества ===
def parse_quantity(val):
    if not val:
        return 0
    try:
        if isinstance(val, (int, float)):
            return int(round(float(val)))
        val = str(val).strip().strip('+')
        if not val:
            return 0
        return sum(int(round(float(part))) for part in val.split('+') if part.strip())
    except:
        return 0

# === Управление параметрами ===
st.markdown("### 🔧 Параметры подбора")

col1, col2 = st.columns(2)
with col1:
    connection = st.radio(
        "Подключение",
        ["VK-правое", "VK-левое", "K-боковое"],
        index=["VK-правое", "VK-левое", "K-боковое"].index(st.session_state.connection),
        horizontal=True
    )
    st.session_state.connection = connection

    types = ["10", "11", "30", "33"] if connection == "VK-левое" else ["10", "11", "20", "21", "22", "30", "33"]
    
    # Проверяем, что текущее значение radiator_type доступно в списке types
    if st.session_state.radiator_type not in types:
        # Если нет, сбрасываем на первое доступное значение
        st.session_state.radiator_type = types[0]
    
    rad_type = st.radio(
        "Тип радиатора",
        types,
        index=types.index(st.session_state.radiator_type),
        horizontal=True
    )
    st.session_state.radiator_type = rad_type

with col2:
    bracket = st.radio(
        "Крепление",
        ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"],
        index=["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"].index(st.session_state.bracket_type)
    )
    st.session_state.bracket_type = bracket

    rad_disc = st.number_input(
        "Скидка на радиаторы, %",
        0.0, 100.0, st.session_state.radiator_discount, 1.0
    )
    br_disc = st.number_input(
        "Скидка на кронштейны, %",
        0.0, 100.0, st.session_state.bracket_discount, 1.0
    )
    st.session_state.radiator_discount = rad_disc
    st.session_state.bracket_discount = br_disc

# === Матрица ===
st.markdown("### 📊 Матрица радиаторов")
sheet_name = f"{st.session_state.connection} {st.session_state.radiator_type}"
if sheet_name not in sheets:
    st.error(f"Лист '{sheet_name}' не найден")
else:
    df = sheets[sheet_name]
    lengths = list(range(400, 2100, 100))
    heights = [300, 400, 500, 600, 900]

    # Заголовки
    cols = st.columns(len(heights) + 1)
    cols[0].markdown("**длина\\высота**")
    for j, h in enumerate(heights):
        cols[j+1].markdown(f"**{h}**", unsafe_allow_html=True)

    has_any = any(st.session_state.entry_values.values())
    for i, l in enumerate(lengths):
        cols = st.columns(len(heights) + 1)
        cols[0].markdown(f"**{l}**", unsafe_allow_html=True)
        for j, h in enumerate(heights):
            pattern = f"/{h}/{l}"
            match = df[df['Наименование'].str.contains(pattern, na=False)]
            if not match.empty:
                art = str(match.iloc[0]['Артикул'])
                key = (sheet_name, art)
                current = st.session_state.entry_values.get(key, "")
                with cols[j+1]:
                    new_val = st.text_input(
                        "",
                        value=current,
                        key=f"cell_{sheet_name}_{art}",
                        label_visibility="collapsed"
                    )
                    if validate_input(new_val):
                        st.session_state.entry_values[key] = new_val
                    else:
                        st.session_state.entry_values[key] = ""