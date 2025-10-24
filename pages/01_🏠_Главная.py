import streamlit as st
import pandas as pd
import re
from utils.session_manager import init_session_state

# Инициализация состояния
init_session_state()

# Загрузка данных
@st.cache_data
def load_sheets():
    sheets = pd.read_excel("data/Матрица.xlsx", sheet_name=None, engine="openpyxl")
    sheets.pop("Кронштейны", None)  # Убираем лист кронштейнов из матрицы
    return sheets

sheets = load_sheets()

# Параметры подключения и типов
CONNECTIONS = ["VK-правое", "VK-левое", "K-боковое"]
RADIATOR_TYPES = {
    "VK-левое": ["10", "11", "30", "33"],
    "VK-правое": ["10", "11", "20", "21", "22", "30", "33"],
    "K-боковое": ["10", "11", "20", "21", "22", "30", "33"],
}

# === Боковая панель ===
with st.sidebar:
    st.image("assets/Lagar.png", width=150)
    st.markdown("### 🔧 ПАРАМЕТРЫ ПОДБОРА")

    connection = st.radio(
        "Подключение:",
        options=CONNECTIONS,
        format_func=lambda x: x.replace("VK-", "VK-нижнее ").replace("K-", "K-боковое"),
        key="connection"
    )

    available_types = RADIATOR_TYPES[connection]
    radiator_type = st.radio("Тип радиатора:", available_types, key="radiator_type")

    bracket_type = st.radio(
        "Крепление:",
        ["Настенные кронштейны", "Напольные кронштейны", "Без кронштейнов"],
        key="bracket_type"
    )

    col1, col2 = st.columns(2)
    with col1:
        radiator_discount = st.number_input("Скидка на радиаторы, %:", min_value=0.0, max_value=100.0, step=1.0, key="radiator_discount")
    with col2:
        bracket_discount = st.number_input("Скидка на кронштейны, %:", min_value=0.0, max_value=100.0, step=1.0, key="bracket_discount")

# === Матрица ===
st.title("RadiaTool Pro v2.0")
st.markdown("#### Матрица радиаторов")

heights = [300, 400, 500, 600, 900]
lengths = list(range(400, 2100, 100))  # 400–2000 с шагом 100

sheet_key = f"{connection} {radiator_type}"
if sheet_key not in sheets:
    st.error(f"Лист '{sheet_key}' не найден в файле Матрица.xlsx")
    st.stop()

df_sheet = sheets[sheet_key]

# Создаём словарь: (длина, высота) → артикул и данные
product_map = {}
for _, row in df_sheet.iterrows():
    name = str(row["Наименование"])
    match = re.search(r"/(\d+)/(\d+)\s*мм", name)
    if match:
        h, l = int(match.group(1)), int(match.group(2))
        product_map[(l, h)] = {
            "артикул": str(row["Артикул"]).strip(),
            "мощность": row.get("Мощность, Вт", ""),
            "вес": row.get("Вес, кг", 0),
            "объём": row.get("Объем, м3", 0),
            "цена": row.get("Цена, руб", 0),
        }

# Заголовки столбцов (высоты)
cols = st.columns([1] + [1] * len(heights))
cols[0].markdown("**Длина \\ Высота**")
for j, h in enumerate(heights):
    cols[j + 1].markdown(f"**{h}**", help="Высота радиатора, мм")

# Строка для каждой длины
for i, length in enumerate(lengths):
    cols = st.columns([1] + [1] * len(heights))
    cols[0].markdown(f"**{length}**", help="Длина радиатора, мм")
    for j, height in enumerate(heights):
        key = (sheet_key, length, height)
        product = product_map.get((length, height))

        if product:
            art = product["артикул"]
            value = st.session_state.entry_values.get((sheet_key, art), "")
            tooltip = (
                f"Артикул: {art}\n"
                f"Мощность: {product['мощность']} Вт\n"
                f"Вес: {product['вес']} кг\n"
                f"Объём: {product['объём']} м³\n"
                f"Цена: {product['цена']} руб"
            )
            with cols[j + 1]:
                user_input = st.text_input(
                    label="",
                    value=str(value),
                    key=f"input_{sheet_key}_{length}_{height}",
                    help=tooltip,
                    label_visibility="collapsed",
                )
                # Валидация: только цифры и +
                if user_input and not re.fullmatch(r"[\d+]*", user_input):
                    st.warning("Только цифры и '+'", icon="⚠️")
                else:
                    if user_input != value:
                        st.session_state.entry_values[(sheet_key, art)] = user_input
                    # Подсветка
                    if user_input:
                        st.markdown('<style>div[data-baseweb="input"] input { background-color: #e6f3ff; }</style>', unsafe_allow_html=True)
        else:
            cols[j + 1].markdown("—")