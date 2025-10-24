# pages/02_📋_Спецификация.py
import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np

# Загрузка данных
@st.cache_data
def load_data():
    matrix_path = Path("data/Матрица.xlsx")
    brackets_path = Path("data/Кронштейны.xlsx")
    sheets = pd.read_excel(matrix_path, sheet_name=None, engine="openpyxl")
    brackets_df = pd.read_excel(brackets_path, engine="openpyxl")
    return sheets, brackets_df

sheets, brackets_df = load_data()

# Функции из tkinter приложения
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

def calculate_brackets(radiator_type, length, height, bracket_type, qty_radiator=1):
    """
    Рассчитывает необходимые кронштейны для радиатора
    
    Параметры:
        radiator_type (str): Тип радиатора ("10", "11", "20" и т.д.)
        length (int): Длина радиатора в мм (400-2000)
        height (int): Высота радиатора в мм (300,400,500,600,900)
        bracket_type (str): Тип крепления
        qty_radiator (int): Количество радиаторов (по умолчанию 1)
    
    Возвращает:
        list: Список кортежей (артикул, количество)
    """
    brackets = []
    
    # Настенные кронштейны
    if bracket_type == "Настенные кронштейны":
        if radiator_type in ["10", "11"]:
            brackets.extend([
                ("К9.2L", 2 * qty_radiator),
                ("К9.2R", 2 * qty_radiator)
            ])
            if 1700 <= length <= 2000:
                brackets.append(("К9.3-40", 1 * qty_radiator))
        
        elif radiator_type in ["20", "21", "22", "30", "33"]:
            art_map = {
                300: "К15.4300",
                400: "К15.4400", 
                500: "К15.4500",
                600: "К15.4600",
                900: "К15.4900"
            }
            if height in art_map:
                art = art_map[height]
                if 400 <= length <= 1600:
                    qty = 2 * qty_radiator
                elif 1700 <= length <= 2000:
                    qty = 3 * qty_radiator
                else:
                    qty = 0
                if qty > 0:
                    brackets.append((art, qty))
    
    # Напольные кронштейны
    elif bracket_type == "Напольные кронштейны":
        if radiator_type in ["10", "11"]:
            if 300 <= height <= 400:
                main_art = "КНС450"
            elif 500 <= height <= 600:
                main_art = "КНС470" 
            elif height == 900:
                main_art = "КНС4100"
            else:
                main_art = None
            
            if main_art:
                brackets.append((main_art, 2 * qty_radiator))
                if 1700 <= length <= 2000:
                    brackets.append(("КНС430", 1 * qty_radiator))
        
        elif radiator_type == "21":
            if 300 <= height <= 400:
                art = "КНС650"
            elif 500 <= height <= 600:
                art = "КНС670"
            elif height == 900:
                art = "КНС6100"
            else:
                art = None
            
            if art:
                if 400 <= length <= 1000:
                    qty = 2 * qty_radiator
                elif 1100 <= length <= 1600:
                    qty = 3 * qty_radiator
                elif 1700 <= length <= 2000:
                    qty = 4 * qty_radiator
                else:
                    qty = 0
                if qty > 0:
                    brackets.append((art, qty))
        
        elif radiator_type in ["20", "22", "30", "33"]:
            if 300 <= height <= 400:
                art = "КНС550"
            elif 500 <= height <= 600:
                art = "КНС570"
            elif height == 900:
                art = "КНС5100"
            else:
                art = None
            
            if art:
                if 400 <= length <= 1000:
                    qty = 2 * qty_radiator
                elif 1100 <= length <= 1600:
                    qty = 3 * qty_radiator
                elif 1700 <= length <= 2000:
                    qty = 4 * qty_radiator
                else:
                    qty = 0
                if qty > 0:
                    brackets.append((art, qty))
    
    return brackets

def calculate_total_power(spec_data):
    """Рассчитывает суммарную мощность (Вт) с учетом количества"""
    total_power = 0.0
    
    for index, row in spec_data.iterrows():
        # Пропуск итоговой строки
        if row["№"] == "Итого":
            continue
            
        # Получение значений из строки
        power_str = str(row["Мощность, Вт"]).strip()
        qty = row["Кол-во"]
        
        try:
            # Конвертация мощности в число
            power = float(power_str) if power_str not in ['', 'nan', 'None'] else 0.0
            
            # Расчет и суммирование
            if power >= 0 and qty >= 0:
                total_power += power * qty
            else:
                print(f"Некорректные значения в строке {index}: мощность={power}, количество={qty}")
                
        except ValueError:
            print(f"Ошибка конвертации мощности в строке {index}: '{power_str}'")
        except TypeError:
            print(f"Неправильный тип данных в строке {index}")
    
    return round(total_power, 2)  # Округление до 2 знаков

def calculate_total_weight_and_volume(spec_data, sheets):
    """
    Рассчитывает общий вес и объем радиаторов (без учета кронштейнов)
    Возвращает:
        total_weight (float): Суммарный вес в кг
        total_volume (float): Суммарный объем в м³
    """
    total_weight = 0.0
    total_volume = 0.0
    
    # Перебираем все строки в спецификации
    for index, row in spec_data.iterrows():
        # Пропускаем строку "Итого" и кронштейны
        if row["№"] == "Итого" or "Кронштейн" in str(row["Наименование"]):
            continue
        
        # Получаем артикул и количество
        art = str(row["Артикул"]).strip()
        qty = int(row["Кол-во"])
        
        # Ищем радиатор в данных
        for sheet_name, data in sheets.items():
            # Проверяем наличие артикула в текущем листе
            product = data[data["Артикул"].str.strip() == art]
            if not product.empty:
                # Суммируем вес и объем
                total_weight += float(product.iloc[0]["Вес, кг"]) * qty
                total_volume += float(product.iloc[0]["Объем, м3"]) * qty
                break  # Прерываем поиск после нахождения
    
    # Округляем значения как в образце
    return round(total_weight, 1), round(total_volume, 3)

def format_power(power_w):
    """
    Форматирует мощность с автоматическим выбором единиц измерения:
    - Если больше или равно 1 000 000 Вт -> переводит в МВт
    - Если больше или равно 1 000 Вт -> переводит в кВт
    - Меньше 1 000 Вт -> оставляет в Вт
    Возвращает строку с единицей измерения.
    """
    try:
        power_w = float(power_w)  # На случай, если передали строку
        
        # Проверяем для МВт (от 1 000 000 Вт)
        if power_w >= 1_000_000:
            power_value = power_w / 1_000_000
            # Округляем до 3 знаков после запятой
            return f"{round(power_value, 3)} МВт"
            
        # Проверяем для кВт (от 1 000 Вт)
        elif power_w >= 1_000:
            power_value = power_w / 1_000
            # Округляем до 3 знаков после запятой
            return f"{round(power_value, 3)} кВт"
            
        # Для значений меньше 1 000 Вт
        else:
            # Округляем до 2 знаков после запятой
            return f"{round(power_w, 2)} Вт"
            
    except (ValueError, TypeError):
        # Если возникла ошибка преобразования
        return f"{power_w} Вт"  # Возвращаем как есть с пометкой Вт

def format_weight(weight_kg):
    """Форматирует вес с автоматическим выбором единиц измерения"""
    if weight_kg >= 1000:  # Более 1000 кг = 1 т
        return f"{weight_kg / 1000:.3f} т"
    else:
        return f"{weight_kg:.3f} кг"

def prepare_spec_data(entry_values, sheets, brackets_df, radiator_discount, bracket_discount, bracket_type):
    """Полная подготовка данных спецификации как в tkinter-приложении"""
    spec_data = []
    radiator_data = []
    bracket_data = []
    brackets_temp = {}

    # Обработка радиаторов
    for key, value in entry_values.items():
        if value and value != "0":
            # Восстанавливаем sheet_name и art из ключа
            parts = key.split('_', 2)
            if len(parts) >= 3:
                sheet_name = f"{parts[0]} {parts[1]}"
                art = parts[2]
                
                if sheet_name in sheets:
                    try:
                        # Получаем значение из entry_values (может быть "1+3")
                        raw_value = value
                        # Вычисляем сумму только при формировании спецификации
                        qty_radiator = parse_quantity(raw_value)
                        mask = sheets[sheet_name]['Артикул'] == art
                        product = sheets[sheet_name].loc[mask]
                        
                        if product.empty:
                            continue
                        
                        product = product.iloc[0]
                        radiator_type = sheet_name.split()[-1]
                        price = float(product['Цена, руб'])
                        # Получаем скидку из переменной интерфейса
                        discount = float(radiator_discount) if radiator_discount else 0.0
                        discounted_price = round(price * (1 - discount / 100), 2)
                        total = round(discounted_price * qty_radiator, 2)
                        
                        # Извлекаем параметры для сортировки из наименования
                        name_parts = product['Наименование'].split('/')
                        height = int(name_parts[-2].replace('мм', '').strip())
                        length = int(name_parts[-1].replace('мм', '').strip().split()[0])
                        
                        # Определяем Вид подключения для сортировки
                        connection_type = "VK" if "VK" in sheet_name else "K"
                        
                        radiator_data.append({
                            "№": len(radiator_data) + 1,
                            "Артикул": str(product['Артикул']).strip(),
                            "Наименование": str(product['Наименование']),
                            "Мощность, Вт": float(product.get('Мощность, Вт', 0)),
                            "Цена, руб (с НДС)": float(price),
                            "Скидка, %": float(discount),
                            "Цена со скидкой, руб (с НДС)": float(discounted_price),
                            "Кол-во": int(qty_radiator),
                            "Сумма, руб (с НДС)": float(total),
                            "ConnectionType": connection_type,  # Для группировки VK/K
                            "RadiatorType": int(radiator_type),  # Тип радиатора (10, 11, 20 и т.д.)
                            "Height": height,  # Высота для сортировки
                            "Length": length  # Длина для сортировки
                        })

                        # Обработка кронштейнов
                        if bracket_type != "Без кронштейнов":
                            brackets = calculate_brackets(
                                radiator_type=radiator_type,
                                length=length,
                                height=height,
                                bracket_type=bracket_type,
                                qty_radiator=qty_radiator
                            )
                            
                            for art_bracket, qty_bracket in brackets:
                                mask_bracket = brackets_df['Артикул'] == art_bracket
                                bracket_info = brackets_df.loc[mask_bracket]
                                
                                if bracket_info.empty:
                                    continue
                                    
                                key = art_bracket.strip()
                                if key not in brackets_temp:
                                    brackets_temp[key] = {
                                        "Артикул": art_bracket,
                                        "Наименование": str(bracket_info.iloc[0]['Наименование']),
                                        "Цена, руб (с НДС)": float(bracket_info.iloc[0]['Цена, руб']),
                                        "Кол-во": 0,
                                        "Сумма, руб (с НДС)": 0.0
                                    }
                                
                                price_bracket = float(bracket_info.iloc[0]['Цена, руб'])
                                # Получаем скидку на кронштейны из переменной интерфейса
                                discount_bracket = float(bracket_discount) if bracket_discount else 0.0
                                discounted_price_bracket = round(price_bracket * (1 - discount_bracket / 100), 2)
                                qty_total = qty_bracket
                                
                                brackets_temp[key]["Кол-во"] += int(qty_total)
                                brackets_temp[key]["Сумма, руб (с НДС)"] += round(discounted_price_bracket * qty_total, 2)

                    except Exception as e:
                        print(f"Ошибка в данных радиатора: {str(e)}")
                        continue

    # Формирование данных кронштейнов
    if brackets_temp:
        for b in brackets_temp.values():
            bracket_discount_val = float(bracket_discount) if bracket_discount else 0.0
            price_with_discount = round(float(b["Цена, руб (с НДС)"]) * (1 - bracket_discount_val / 100), 2)
            
            bracket_data.append({
                "№": len(radiator_data) + len(bracket_data) + 1,
                "Артикул": str(b["Артикул"]),
                "Наименование": str(b["Наименование"]),
                "Мощность, Вт": 0.0,
                "Цена, руб (с НДС)": float(b["Цена, руб (с НДС)"]),
                "Скидка, %": float(bracket_discount_val),
                "Цена со скидкой, руб (с НДС)": float(price_with_discount),
                "Кол-во": int(b["Кол-во"]),
                "Сумма, руб (с НДС)": float(b["Сумма, руб (с НДС)"]),
                "ConnectionType": "Bracket"  # Для кронштейнов
            })

    # Сортировка радиаторов: сначала VK, потом K, затем по типу, высоте, длине
    radiator_data_sorted = sorted(
        radiator_data, 
        key=lambda x: (
            0 if x["ConnectionType"] == "VK" else 1,  # Сначала VK, потом K
            x["RadiatorType"],  # Затем по типу радиатора (10, 11, 20...)
            x["Height"],  # Затем по высоте
            x["Length"]  # Затем по длине
        )
    )
    
    # Обновляем номера после сортировки
    for i, item in enumerate(radiator_data_sorted, 1):
        item["№"] = i
    
    # Объединение данных (отсортированные радиаторы + кронштейны)
    combined_data = radiator_data_sorted + bracket_data
    
    if not combined_data:
        return pd.DataFrame()

    # Создание DataFrame (удаляем временные поля для сортировки)
    df = pd.DataFrame(
        combined_data,
        columns=[
            "№", "Артикул", "Наименование", "Мощность, Вт",
            "Цена, руб (с НДС)", "Скидка, %",
            "Цена со скидкой, руб (с НДС)", "Кол-во",
            "Сумма, руб (с НДС)"
        ]
    )
    
    return df

def add_total_row(spec_data):
    """Добавляет итоговую строку к данным спецификации"""
    total_sum = spec_data["Сумма, руб (с НДС)"].sum()
    total_qty_radiators = sum(spec_data[~spec_data["Наименование"].str.contains("Кронштейн", na=False)]["Кол-во"])
    total_qty_brackets = sum(spec_data[spec_data["Наименование"].str.contains("Кронштейн", na=False)]["Кол-во"])
    
    total_row = pd.DataFrame([{
        "№": "Итого",
        "Артикул": "",
        "Наименование": "",
        "Мощность, Вт": "",
        "Цена, руб (с НДС)": "",
        "Скидка, %": "",
        "Цена со скидкой, руб (с НДС)": "",
        "Кол-во": f"{total_qty_radiators} / {total_qty_brackets}",
        "Сумма, руб (с НДС)": f"{total_sum:.2f}"
    }])
    
    return pd.concat([spec_data, total_row], ignore_index=True)

# Интерфейс
st.title("📋 Спецификация")

# Инициализация session_state если не существует
if "entry_values" not in st.session_state:
    st.session_state.entry_values = {}
if "radiator_discount" not in st.session_state:
    st.session_state.radiator_discount = 0.0
if "bracket_discount" not in st.session_state:
    st.session_state.bracket_discount = 0.0
if "bracket_type" not in st.session_state:
    st.session_state.bracket_type = "Настенные кронштейны"

# Проверяем есть ли заполненные значения
has_values = any(val and val != "0" for val in st.session_state.entry_values.values())

if not has_values:
    st.info("Заполните матрицу на странице 'Главная', чтобы сформировать спецификацию.")
else:
    # Подготавливаем данные спецификации
    spec_data = prepare_spec_data(
        st.session_state.entry_values,
        sheets,
        brackets_df,
        st.session_state.radiator_discount,
        st.session_state.bracket_discount,
        st.session_state.bracket_type
    )
    
    if spec_data.empty:
        st.warning("Нет данных для отображения.")
    else:
        # Добавляем итоговую строку
        spec_data_with_total = add_total_row(spec_data)
        
        # Отображаем таблицу
        st.dataframe(
            spec_data_with_total,
            use_container_width=True,
            hide_index=True,
            column_config={
                "№": st.column_config.TextColumn("№", width="small"),
                "Артикул": st.column_config.TextColumn("Артикул", width="small"),
                "Наименование": st.column_config.TextColumn("Наименование", width="large"),
                "Мощность, Вт": st.column_config.NumberColumn("Мощность, Вт", format="%.2f", width="small"),
                "Цена, руб (с НДС)": st.column_config.NumberColumn("Цена, руб (с НДС)", format="%.2f", width="medium"),
                "Скидка, %": st.column_config.NumberColumn("Скидка, %", format="%.2f", width="small"),
                "Цена со скидкой, руб (с НДС)": st.column_config.NumberColumn("Цена со скидкой, руб (с НДС)", format="%.2f", width="medium"),
                "Кол-во": st.column_config.NumberColumn("Кол-во", format="%d", width="small"),
                "Сумма, руб (с НДС)": st.column_config.NumberColumn("Сумма, руб (с НДС)", format="%.2f", width="medium")
            }
        )
        
        # Расчет итоговых значений
        total_power = calculate_total_power(spec_data)
        total_weight, total_volume = calculate_total_weight_and_volume(spec_data, sheets)
        total_sum = spec_data["Сумма, руб (с НДС)"].sum()
        
        # Отображаем итоговую информацию
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Суммарная мощность", format_power(total_power))
        
        with col2:
            st.metric("Общий вес", format_weight(total_weight))
        
        with col3:
            st.metric("Общий объем", f"{total_volume:.3f} м³")
        
        st.metric("Общая сумма спецификации", f"{total_sum:.2f} руб")
        
        # Кнопка экспорта
        if st.button("💾 Экспорт в Excel"):
            # Здесь можно добавить функциональность экспорта
            st.success("Функциональность экспорта будет добавлена в следующем обновлении")