# pages/03_📊_Импорт_данных.py
import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from pathlib import Path
import io

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
if "entry_values" not in st.session_state:
    st.session_state.entry_values = {}
if "mappings" not in st.session_state:
    st.session_state.mappings = {}
if "correspondence_data" not in st.session_state:
    st.session_state.correspondence_data = None

# === Функции импорта ===
def parse_quantity(value):
    """Преобразует значение в количество"""
    try:
        if not value:
            return 0
        if isinstance(value, (int, float)):
            return int(round(float(value)))
        value = str(value).strip()
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
    except Exception:
        return 0

def load_mappings():
    """Загружает сохраненные соответствия"""
    mappings_file = Path("data/mappings.json")
    if mappings_file.exists():
        try:
            with open(mappings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mappings(mappings):
    """Сохраняет соответствия"""
    mappings_file = Path("data/mappings.json")
    mappings_file.parent.mkdir(exist_ok=True)
    with open(mappings_file, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, ensure_ascii=False, indent=2)

def find_meteor_analog(competitor_name, qty):
    """Находит аналог METEOR для радиатора конкурента"""
    # Сначала проверяем сохраненные соответствия
    mappings = load_mappings()
    if competitor_name in mappings:
        mapping = mappings[competitor_name]
        sheet_name = f"{mapping['connection']} {mapping['rad_type']}"
        art = mapping['meteor_art']
        
        # Добавляем в текущие значения
        simple_key = f"{sheet_name.replace(' ', '_')}_{art}"
        current_qty = parse_quantity(st.session_state.entry_values.get(simple_key, "0"))
        st.session_state.entry_values[simple_key] = str(current_qty + qty)
        return True, mapping['meteor_name'], art
    
    # Если соответствие не найдено, пытаемся автоматически определить
    meteor_match = None
    
    # Шаблоны для распознавания
    patterns = [
        # Панельный стальной радиатор Valve Compact тип VС 22-500-600
        re.compile(r'(?:радиатор|radiator).*?тип\s*([ckv])\s*(\d+)[-\s](\d+)[-\s](\d+)', re.IGNORECASE),
        # Радиаторы стальные штампованные "Лидея" ЛК 11-504
        re.compile(r'(?:радиатор|radiator).*?[лl][кk]\s*(\d+)[-\s](\d+)', re.IGNORECASE),
        # VC 22-500-600
        re.compile(r'([ckv])\s*(\d+)[-\s](\d+)[-\s](\d+)', re.IGNORECASE),
        # ЛК 11-504
        re.compile(r'[лl][кk]\s*(\d+)[-\s](\d+)', re.IGNORECASE)
    ]
    
    for pattern in patterns:
        match = pattern.search(competitor_name)
        if match:
            meteor_match = match
            break
    
    if meteor_match:
        # Определяем параметры
        if meteor_match.re == patterns[0] or meteor_match.re == patterns[2]:
            connection_type = meteor_match.group(1).upper()
            rad_type = meteor_match.group(2)
            height = int(meteor_match.group(3))
            length = int(meteor_match.group(4))
            
            if connection_type in ['V', 'C']:
                connection = "VK-правое"
            else:
                connection = "K-боковое"
                
        elif meteor_match.re == patterns[1] or meteor_match.re == patterns[3]:
            rad_type = meteor_match.group(1)
            length = int(meteor_match.group(2))
            
            if rad_type in ['11', '22', '33']:
                height = 500
                connection = "VK-правое"
            else:
                height = 500
                connection = "VK-правое"
        
        # Ищем радиатор в данных METEOR
        sheet_name = f"{connection} {rad_type}"
        if sheet_name in sheets:
            data = sheets[sheet_name]
            pattern = f"/{height}/{length}"
            match = data[data['Наименование'].str.contains(pattern, na=False)]
            
            if not match.empty:
                product = match.iloc[0]
                art = str(product['Артикул']).strip()
                
                # Добавляем в текущие значения
                simple_key = f"{sheet_name.replace(' ', '_')}_{art}"
                current_qty = parse_quantity(st.session_state.entry_values.get(simple_key, "0"))
                st.session_state.entry_values[simple_key] = str(current_qty + qty)
                
                return True, product['Наименование'], art
    
    return False, "", ""

def import_meteor_excel(uploaded_file):
    """Импорт из Excel спецификации METEOR"""
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
        
        # Поиск столбцов с артикулами и количеством
        art_col = None
        qty_col = None
        header_row = 0
        
        for i, row in df.iterrows():
            for j, cell in enumerate(row):
                cell_str = str(cell).strip().lower()
                
                if not art_col and any(x in cell_str for x in ['артикул', 'art', 'код']):
                    art_col = j
                if not qty_col and any(x in cell_str for x in ['кол-во', 'количество', 'qty']):
                    qty_col = j
            
            if art_col is not None and qty_col is not None:
                header_row = i
                break
        
        if art_col is None:
            art_col = 0
        if qty_col is None:
            qty_col = 1 if len(df.columns) > 1 else 0
        
        # Обработка данных
        total_loaded = 0
        total_qty = 0
        
        for i in range(header_row + 1, len(df)):
            art = str(df.iloc[i, art_col]).strip()
            qty = df.iloc[i, qty_col]
            
            if not art or art.lower() == 'итого':
                continue
                
            try:
                qty = float(qty)
                if qty > 0:
                    # Ищем артикул в данных
                    found = False
                    for sheet_name, sheet_data in sheets.items():
                        if art in sheet_data['Артикул'].astype(str).str.strip().values:
                            simple_key = f"{sheet_name.replace(' ', '_')}_{art}"
                            current_qty = parse_quantity(st.session_state.entry_values.get(simple_key, "0"))
                            st.session_state.entry_values[simple_key] = str(current_qty + int(qty))
                            total_loaded += 1
                            total_qty += int(qty)
                            found = True
                            break
                    
                    if not found:
                        st.warning(f"Артикул не найден: {art}")
                        
            except (ValueError, TypeError):
                continue
        
        return True, f"Успешно загружено: {total_loaded} позиций\nОбщее количество: {total_qty}"
        
    except Exception as e:
        return False, f"Ошибка загрузки Excel: {str(e)}"

def import_meteor_csv(uploaded_file):
    """Импорт из CSV файла METEOR"""
    try:
        # Пробуем разные кодировки
        content = uploaded_file.getvalue().decode('utf-8-sig')
        df = pd.read_csv(io.StringIO(content), sep=';', header=None)
        
        # Проверяем наличие заголовков
        has_headers = not df.iloc[0, 0].replace('.', '').isdigit()
        
        if has_headers:
            df = pd.read_csv(io.StringIO(content), sep=';', header=0)
        else:
            df.columns = ['Артикул', 'Кол-во']
        
        df = df[df.iloc[:, 0].notna()]
        
        # Определяем столбцы
        art_col = None
        qty_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'артикул' in col_lower or 'art' in col_lower or 'код' in col_lower:
                art_col = col
            elif 'кол-во' in col_lower or 'количество' in col_lower or 'qty' in col_lower:
                qty_col = col
        
        if art_col is None:
            art_col = df.columns[0]
        if qty_col is None:
            qty_col = df.columns[1] if len(df.columns) > 1 else None
        
        if qty_col is None:
            return False, "Не найден столбец с количеством"
        
        # Обработка данных
        df[art_col] = df[art_col].astype(str).str.replace(' ', '').str.strip()
        df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0).astype(int)
        
        # Группируем и суммируем
        grouped_df = df.groupby(art_col)[qty_col].sum().reset_index()
        
        total_loaded = 0
        total_qty = 0
        
        for _, row in grouped_df.iterrows():
            art = str(row[art_col]).strip()
            qty = int(row[qty_col])
            
            found = False
            for sheet_name, sheet_data in sheets.items():
                mask = sheet_data['Артикул'].astype(str).str.strip() == art
                if mask.any():
                    simple_key = f"{sheet_name.replace(' ', '_')}_{art}"
                    current_qty = parse_quantity(st.session_state.entry_values.get(simple_key, "0"))
                    st.session_state.entry_values[simple_key] = str(current_qty + qty)
                    total_loaded += 1
                    total_qty += qty
                    found = True
                    break
            
            if not found:
                st.warning(f"Артикул не найден: {art}")
        
        return True, f"Успешно загружено: {total_loaded} позиций\nОбщее количество: {total_qty}"
        
    except Exception as e:
        return False, f"Ошибка загрузки CSV: {str(e)}"

def import_foreign_spec(uploaded_file, file_type):
    """Импорт из спецификации других производителей"""
    try:
        if file_type == "excel":
            df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
        else:  # CSV
            content = uploaded_file.getvalue().decode('utf-8-sig')
            df = pd.read_csv(io.StringIO(content), sep=';', header=None)
        
        # Поиск столбцов
        name_col = None
        qty_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'наименование' in col_lower or 'name' in col_lower or 'описание' in col_lower:
                name_col = col
            elif 'кол-во' in col_lower or 'количество' in col_lower or 'qty' in col_lower:
                qty_col = col
        
        if name_col is None:
            name_col = df.columns[0]
        if qty_col is None:
            qty_col = df.columns[1] if len(df.columns) > 1 else None
        
        if qty_col is None:
            return False, "Не найден столбец с количеством"
        
        # Обработка данных
        correspondence_data = []
        total_loaded = 0
        total_qty = 0
        not_found = []
        
        for _, row in df.iterrows():
            try:
                name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
                
                qty = 0
                if pd.notna(row[qty_col]):
                    try:
                        qty_val = row[qty_col]
                        if isinstance(qty_val, str):
                            qty_val = qty_val.replace(',', '.').strip()
                        qty = int(float(qty_val)) if str(qty_val).strip() else 0
                    except (ValueError, TypeError):
                        qty = 0
                
                if qty <= 0 or not name:
                    continue
                
                # Пропускаем нерадиаторы
                if not any(x in name.lower() for x in ['радиатор', 'radiator', 'k-profil', 'vk-profil']):
                    continue
                
                # Ищем аналог
                found, meteor_name, meteor_art = find_meteor_analog(name, qty)
                
                if found:
                    correspondence_data.append({
                        "Оригинальное наименование": name,
                        "Количество": qty,
                        "Аналог Meteor": meteor_name,
                        "Артикул Meteor": meteor_art,
                        "Комментарий": "Автоматически определен"
                    })
                    total_loaded += 1
                    total_qty += qty
                else:
                    not_found.append(name)
                    correspondence_data.append({
                        "Оригинальное наименование": name,
                        "Количество": qty,
                        "Аналог Meteor": "",
                        "Артикул Meteor": "",
                        "Комментарий": "Не найден аналог"
                    })
                    
            except Exception as e:
                continue
        
        # Сохраняем данные соответствия
        if correspondence_data:
            st.session_state.correspondence_data = pd.DataFrame(correspondence_data)
        
        # Формируем сообщение о результате
        msg = f"Успешно загружено: {total_loaded} позиций\nОбщее количество: {total_qty}"
        
        if not_found:
            msg += f"\n\nНе найдены аналоги для {len(not_found)} позиций"
            if len(not_found) <= 5:
                msg += ":\n" + "\n".join(f"- {item}" for item in not_found[:5])
            else:
                msg += f" (первые 5):\n" + "\n".join(f"- {item}" for item in not_found[:5])
        
        return True, msg
        
    except Exception as e:
        return False, f"Ошибка загрузки файла: {str(e)}"

# === Интерфейс страницы ===
st.title("📊 Импорт данных")

st.info("""
Загрузите спецификации для автоматического подбора радиаторов METEOR.
Поддерживаются файлы Excel (.xlsx, .xls) и CSV.
""")

# Создаем вкладки для разных типов импорта
tab1, tab2, tab3 = st.tabs([
    "📋 Спецификация METEOR", 
    "📁 Файл METEOR CSV", 
    "🏭 Другие производители"
])

with tab1:
    st.subheader("Импорт из спецификации METEOR")
    st.write("Загрузите Excel файл со спецификацией METEOR")
    
    uploaded_file = st.file_uploader(
        "Выберите Excel файл", 
        type=["xlsx", "xls"],
        key="excel_upload"
    )
    
    if uploaded_file is not None:
        if st.button("Импортировать из Excel", key="import_excel"):
            with st.spinner("Обработка файла..."):
                success, message = import_meteor_excel(uploaded_file)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab2:
    st.subheader("Импорт из файла METEOR CSV")
    st.write("Загрузите CSV файл со спецификацией METEOR")
    
    uploaded_file = st.file_uploader(
        "Выберите CSV файл", 
        type=["csv"],
        key="csv_upload"
    )
    
    if uploaded_file is not None:
        if st.button("Импортировать из CSV", key="import_csv"):
            with st.spinner("Обработка файла..."):
                success, message = import_meteor_csv(uploaded_file)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab3:
    st.subheader("Импорт спецификаций других производителей")
    st.write("Загрузите файл со спецификацией другого производителя для автоматического подбора аналогов METEOR")
    
    file_type = st.radio(
        "Тип файла",
        ["Excel", "CSV"],
        horizontal=True
    )
    
    uploaded_file = st.file_uploader(
        f"Выберите {file_type} файл", 
        type=["xlsx", "xls", "csv"] if file_type == "Excel" else ["csv"],
        key="foreign_upload"
    )
    
    if uploaded_file is not None:
        if st.button("Импортировать и найти аналоги", key="import_foreign"):
            with st.spinner("Поиск аналогов METEOR..."):
                success, message = import_foreign_spec(uploaded_file, file_type.lower())
                if success:
                    st.success(message)
                    
                    # Показываем таблицу соответствия, если есть данные
                    if st.session_state.correspondence_data is not None:
                        st.subheader("Таблица соответствия")
                        st.dataframe(
                            st.session_state.correspondence_data,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Кнопка сохранения таблицы соответствия
                        if st.button("Сохранить таблицу соответствия"):
                            csv_data = st.session_state.correspondence_data.to_csv(index=False, sep=';', encoding='utf-8-sig')
                            st.download_button(
                                label="📥 Скачать таблицу соответствия",
                                data=csv_data,
                                file_name="Таблица соответствия переподбора на радиаторы METEOR.csv",
                                mime="text/csv"
                            )
                    
                    st.rerun()
                else:
                    st.error(message)

# Информация о текущем состоянии
st.markdown("---")
st.subheader("Текущее состояние")

filled_cells = sum(1 for val in st.session_state.entry_values.values() if val and parse_quantity(val) > 0)
if filled_cells > 0:
    st.success(f"✅ В системе загружено: {filled_cells} позиций")
    
    # Показываем выбранные позиции
    selected_items = []
    for key, value in st.session_state.entry_values.items():
        if value and parse_quantity(value) > 0:
            parts = key.split('_')
            if len(parts) >= 3:
                sheet_name = f"{parts[0]} {parts[1]}"
                art = parts[2]
                
                for sheet, data in sheets.items():
                    if sheet == sheet_name:
                        product = data[data['Артикул'] == art]
                        if not product.empty:
                            selected_items.append({
                                'Артикул': art,
                                'Наименование': product.iloc[0]['Наименование'],
                                'Количество': parse_quantity(value)
                            })
                            break
    
    if selected_items:
        st.write("**Загруженные позиции:**")
        df = pd.DataFrame(selected_items)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Кнопка перехода к главной странице
st.markdown("---")
if st.button("🏠 Перейти к подбору радиаторов"):
    st.switch_page("pages/01_🏠_Главная.py")

# Кнопка очистки данных
if st.button("🗑️ Очистить все загруженные данные"):
    st.session_state.entry_values.clear()
    st.session_state.correspondence_data = None
    st.success("Все данные очищены")
    st.rerun()