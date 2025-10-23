# pages/02_📋_Спецификация.py
import streamlit as st
import pandas as pd
from pathlib import Path

# Загрузка данных
@st.cache_data
def load_data():
    matrix_path = Path("data/Матрица.xlsx")
    brackets_path = Path("data/Кронштейны.xlsx")
    sheets = pd.read_excel(matrix_path, sheet_name=None, engine="openpyxl")
    brackets_df = pd.read_excel(brackets_path, engine="openpyxl")
    return sheets, brackets_df

sheets, brackets_df = load_data()

# Функции расчета
def parse_quantity(val):
    if not val: return 0
    try:
        if isinstance(val, (int, float)): return int(round(float(val)))
        val = str(val).strip().strip('+')
        if not val: return 0
        return sum(int(round(float(part))) for part in val.split('+') if part.strip())
    except:
        return 0

def calculate_brackets(radiator_type, length, height, bracket_type, qty=1):
    brackets = []
    if bracket_type == "Настенные кронштейны":
        if radiator_type in ["10", "11"]:
            brackets.extend([("К9.2L", 2*qty), ("К9.2R", 2*qty)])
            if 1700 <= length <= 2000: brackets.append(("К9.3-40", 1*qty))
        elif radiator_type in ["20", "21", "22", "30", "33"]:
            art_map = {300: "К15.4300", 400: "К15.4400", 500: "К15.4500", 600: "К15.4600", 900: "К15.4900"}
            if height in art_map:
                art = art_map[height]
                qty_br = 2*qty if 400 <= length <= 1600 else (3*qty if 1700 <= length <= 2000 else 0)
                if qty_br: brackets.append((art, qty_br))
    elif bracket_type == "Напольные кронштейны":
        if radiator_type in ["10", "11"]:
            art_map = {300: "КНС450", 400: "КНС450", 500: "КНС470", 600: "КНС470", 900: "КНС4100"}
            main_art = art_map.get(height)
            if main_art:
                brackets.append((main_art, 2*qty))
                if 1700 <= length <= 2000: brackets.append(("КНС430", 1*qty))
        elif radiator_type == "21":
            art_map = {300: "КНС650", 400: "КНС650", 500: "КНС670", 600: "КНС670", 900: "КНС6100"}
            art = art_map.get(height)
            if art:
                if 400 <= length <= 1000: qty_br = 2*qty
                elif 1100 <= length <= 1600: qty_br = 3*qty
                elif 1700 <= length <= 2000: qty_br = 4*qty
                else: qty_br = 0
                if qty_br: brackets.append((art, qty_br))
        elif radiator_type in ["20", "22", "30", "33"]:
            art_map = {300: "КНС550", 400: "КНС550", 500: "КНС570", 600: "КНС570", 900: "КНС5100"}
            art = art_map.get(height)
            if art:
                if 400 <= length <= 1000: qty_br = 2*qty
                elif 1100 <= length <= 1600: qty_br = 3*qty
                elif 1700 <= length <= 2000: qty_br = 4*qty
                else: qty_br = 0
                if qty_br: brackets.append((art, qty_br))
    return brackets

# Формирование спецификации
def prepare_spec():
    spec_data = []
    bracket_temp = {}
    for (sheet_name, art), raw_val in st.session_state.entry_values.items():
        if not raw_val or sheet_name not in sheets:
            continue
        qty = parse_quantity(raw_val)
        if qty <= 0:
            continue
        df = sheets[sheet_name]
        product = df[df['Артикул'] == art]
        if product.empty:
            continue
        product = product.iloc[0]
        rad_type = sheet_name.split()[-1]
        price = float(product['Цена, руб'])
        disc = st.session_state.radiator_discount
        disc_price = round(price * (1 - disc / 100), 2)
        total = round(disc_price * qty, 2)
        name_parts = str(product['Наименование']).split('/')
        height = int(name_parts[-2].replace('мм', '').strip())
        length = int(name_parts[-1].replace('мм', '').strip().split()[0])
        conn_type = "VK" if "VK" in sheet_name else "K"
        spec_data.append({
            "№": len(spec_data) + 1,
            "Артикул": str(product['Артикул']),
            "Наименование": str(product['Наименование']),
            "Мощность, Вт": float(product.get('Мощность, Вт', 0)),
            "Цена, руб (с НДС)": price,
            "Скидка, %": disc,
            "Цена со скидкой, руб (с НДС)": disc_price,
            "Кол-во": qty,
            "Сумма, руб (с НДС)": total,
            "ConnectionType": conn_type,
            "RadiatorType": int(rad_type),
            "Height": height,
            "Length": length
        })
        if st.session_state.bracket_type != "Без кронштейнов":
            brackets = calculate_brackets(rad_type, length, height, st.session_state.bracket_type, qty)
            for art_b, qty_b in brackets:
                b_info = brackets_df[brackets_df['Артикул'] == art_b]
                if b_info.empty:
                    continue
                key = art_b.strip()
                if key not in bracket_temp:
                    bracket_temp[key] = {
                        "Артикул": art_b,
                        "Наименование": str(b_info.iloc[0]['Наименование']),
                        "Цена, руб (с НДС)": float(b_info.iloc[0]['Цена, руб']),
                        "Кол-во": 0,
                        "Сумма, руб (с НДС)": 0.0
                    }
                b_price = float(b_info.iloc[0]['Цена, руб'])
                b_disc = st.session_state.bracket_discount
                b_disc_price = round(b_price * (1 - b_disc / 100), 2)
                bracket_temp[key]["Кол-во"] += qty_b
                bracket_temp[key]["Сумма, руб (с НДС)"] += round(b_disc_price * qty_b, 2)
    spec_data.sort(key=lambda x: (0 if x["ConnectionType"] == "VK" else 1, x["RadiatorType"], x["Height"], x["Length"]))
    for i, item in enumerate(spec_data, 1):
        item["№"] = i
    bracket_list = []
    for b in bracket_temp.values():
        b_disc = st.session_state.bracket_discount
        b_price = b["Цена, руб (с НДС)"]
        b_disc_price = round(b_price * (1 - b_disc / 100), 2)
        bracket_list.append({
            "№": len(spec_data) + len(bracket_list) + 1,
            "Артикул": b["Артикул"],
            "Наименование": b["Наименование"],
            "Мощность, Вт": 0.0,
            "Цена, руб (с НДС)": b_price,
            "Скидка, %": b_disc,
            "Цена со скидкой, руб (с НДС)": b_disc_price,
            "Кол-во": b["Кол-во"],
            "Сумма, руб (с НДС)": b["Сумма, руб (с НДС)"],
            "ConnectionType": "Bracket"
        })
    return pd.DataFrame(spec_data + bracket_list)

# Интерфейс
st.title("📋 Спецификация")

if not st.session_state.entry_values:
    st.info("Заполните матрицу на странице 'Главная', чтобы сформировать спецификацию.")
else:
    df = prepare_spec()
    if df.empty:
        st.warning("Нет данных для отображения.")
    else:
        st.dataframe(df, use_container_width=True)
        total_sum = df["Сумма, руб (с НДС)"].sum()
        total_power = df[df["Мощность, Вт"] > 0]["Мощность, Вт"].sum()
        st.markdown(f"**Суммарная мощность:** {total_power:.2f} Вт")
        st.markdown(f"**Сумма спецификации:** {total_sum:.2f} руб")