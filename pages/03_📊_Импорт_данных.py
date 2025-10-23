# pages/03_📊_Импорт_данных.py
import streamlit as st
import pandas as pd
import io
import re
from utils.session_manager import initialize_session_state, save_mappings
from utils.calculator import parse_quantity

st.set_page_config(
    page_title="Импорт данных - RadiaTool Pro",
    page_icon="📊", 
    layout="wide"
)

def main():
    initialize_session_state()
    
    st.title("📊 Импорт данных")
    st.markdown("---")
    
    # Выбор типа импорта
    import_type = st.radio(
        "**Тип импорта:**",
        ["METEOR спецификация", "Другие производители"],
        horizontal=True,
        key="import_type_radio"
    )
    
    if import_type == "METEOR спецификация":
        import_meteor_spec()
    else:
        import_other_manufacturers()

def import_meteor_spec():
    """Импорт спецификаций METEOR"""
    
    st.subheader("📥 Импорт из METEOR")
    
    uploaded_file = st.file_uploader(
        "**Загрузите файл спецификации**",
        type=['xlsx', 'xls', 'csv'],
        help="Поддерживаются форматы: Excel (.xlsx, .xls), CSV",
        key="meteor_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Чтение файла
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Файл загружен: {uploaded_file.name}")
            
            # Предпросмотр данных
            with st.expander("🔍 Предпросмотр данных", expanded=True):
                st.write(f"**Размер данных:** {len(df)} строк, {len(df.columns)} столбцов")
                st.dataframe(df.head(10), use_container_width=True)
            
            # Автораспознавание столбцов
            art_col, qty_col = detect_columns(df)
            
            if art_col and qty_col:
                st.info(f"📊 Автоматически распознано: Артикул - '{art_col}', Количество - '{qty_col}'")
                
                # Обработка данных
                processed_df = process_meteor_data(df, art_col, qty_col)
                
                if not processed_df.empty:
                    display_processed_data(processed_df, "METEOR")
                    
            else:
                st.error("❌ Не удалось автоматически определить столбцы")
                manual_column_selection(df)
                
        except Exception as e:
            st.error(f"❌ Ошибка загрузки файла: {e}")

def import_other_manufacturers():
    """Импорт данных других производителей"""
    
    st.subheader("🏭 Импорт данных других производителей")
    
    st.info("""
    **🔍 Поддерживаемые форматы наименований:**
    - VC 22-500-600
    - ЛК 11-504  
    - тип 10-400-1000
    - VK 30-600-1200
    """)
    
    uploaded_file = st.file_uploader(
        "**Загрузите файл с наименованиями конкурентов**",
        type=['xlsx', 'xls', 'csv'],
        key="competitor_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Чтение файла
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Файл загружен: {uploaded_file.name}")
            
            # Предпросмотр
            with st.expander("🔍 Предпросмотр данных", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Автораспознавание столбцов
            art_col, qty_col, name_col = detect_competitor_columns(df)
            
            if name_col and qty_col:
                st.info(f"📊 Распознано: Наименование - '{name_col}', Количество - '{qty_col}'")
                
                # Обработка данных конкурентов
                processed_df = process_competitor_data(df, name_col, qty_col)
                
                if not processed_df.empty:
                    display_processed_data(processed_df, "Competitor")
                    
            else:
                st.error("❌ Не удалось автоматически определить столбцы")
                manual_competitor_selection(df)
                
        except Exception as e:
            st.error(f"❌ Ошибка загрузки файла: {e}")

def detect_columns(df):
    """Автораспознавание столбцов для METEOR"""
    art_col, qty_col = None, None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['артикул', 'art', 'код', 'code', 'articul']):
            art_col = col
        elif any(keyword in col_lower for keyword in ['кол-во', 'количество', 'qty', 'quantity', 'count']):
            qty_col = col
    
    return art_col, qty_col

def detect_competitor_columns(df):
    """Автораспознавание столбцов для конкурентов"""
    art_col, qty_col, name_col = None, None, None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['артикул', 'art', 'код', 'code']):
            art_col = col
        elif any(keyword in col_lower for keyword in ['кол-во', 'количество', 'qty', 'quantity']):
            qty_col = col
        elif any(keyword in col_lower for keyword in ['наименование', 'name', 'название', 'product']):
            name_col = col
    
    return art_col, qty_col, name_col

def process_meteor_data(df, art_col, qty_col):
    """Обработка импортированных данных METEOR"""
    try:
        # Базовая очистка
        processed_df = df[[art_col, qty_col]].copy()
        processed_df.columns = ['Артикул', 'Количество']
        
        # Удаление пустых строк
        processed_df = processed_df.dropna()
        
        # Преобразование артикулов к строковому типу
        processed_df['Артикул'] = processed_df['Артикул'].astype(str)
        
        # Преобразование количеств
        processed_df['Количество'] = pd.to_numeric(processed_df['Количество'], errors='coerce')
        processed_df = processed_df.dropna(subset=['Количество'])
        processed_df['Количество'] = processed_df['Количество'].astype(int)
        
        # Суммирование одинаковых артикулов
        processed_df = processed_df.groupby('Артикул', as_index=False)['Количество'].sum()
        
        # Добавление статуса распознавания
        processed_df['Статус'] = processed_df['Артикул'].apply(check_meteor_article)
        
        return processed_df
        
    except Exception as e:
        st.error(f"❌ Ошибка обработки данных: {e}")
        return pd.DataFrame()

def process_competitor_data(df, name_col, qty_col):
    """Обработка данных конкурентов"""
    try:
        # Базовая очистка
        processed_df = df[[name_col, qty_col]].copy()
        processed_df.columns = ['Наименование', 'Количество']
        
        # Удаление пустых строк
        processed_df = processed_df.dropna()
        
        # Преобразование количеств
        processed_df['Количество'] = pd.to_numeric(processed_df['Количество'], errors='coerce')
        processed_df = processed_df.dropna(subset=['Количество'])
        processed_df['Количество'] = processed_df['Количество'].astype(int)
        
        # Парсинг наименований
        processed_df['Параметры'] = processed_df['Наименование'].apply(parse_competitor_name)
        
        # Сопоставление с METEOR
        processed_df['Соответствие METEOR'] = processed_df['Параметры'].apply(map_to_meteor)
        
        return processed_df
        
    except Exception as e:
        st.error(f"❌ Ошибка обработки данных: {e}")
        return pd.DataFrame()

def parse_competitor_name(name):
    """Парсинг наименований конкурентов для автоматического определения параметров"""
    name_str = str(name).upper()
    
    patterns = [
        # VC 22-500-600, VK 30-600-1200
        r'(V[KC])\s*(\d+)[-\s](\d+)[-\s](\d+)',
        # ЛК 11-504, ЛК 11-504-900
        r'[ЛL][КK]\s*(\d+)[-\s](\d+)(?:[-\s](\d+))?',
        # тип 10-400-1000
        r'ТИП\s*(\d+)[-\s](\d+)[-\s](\d+)',
        # 10-400-1000
        r'(\d+)[-\s](\d+)[-\s](\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name_str)
        if match:
            return extract_parameters(match, pattern)
    
    return None

def extract_parameters(match, pattern):
    """Извлечение параметров из regex match"""
    groups = match.groups()
    
    if 'V' in pattern:
        # VK/VC формат: VK 30-600-1200
        return {
            'type': groups[1] if len(groups) >= 2 else None,
            'height': int(groups[2]) if len(groups) >= 3 and groups[2] else None,
            'length': int(groups[3]) if len(groups) >= 4 and groups[3] else None,
            'connection': 'VK-правое' if groups[0] == 'VK' else 'VK-левое'
        }
    else:
        # Другие форматы
        return {
            'type': groups[0] if groups[0] else None,
            'height': int(groups[1]) if len(groups) >= 2 and groups[1] else None,
            'length': int(groups[2]) if len(groups) >= 3 and groups[2] else None,
            'connection': 'K-боковое'
        }

def map_to_meteor(parameters):
    """Сопоставление параметров с артикулами METEOR"""
    if not parameters:
        return "Не распознано"
    
    # Поиск в загруженных данных METEOR
    sheets = st.session_state.sheets
    
    for sheet_name, df in sheets.items():
        # Определение подключения из названия листа
        if parameters.get('connection', '').replace('-', ' ') in sheet_name:
            # Поиск по размерам в наименованиях
            pattern = f"/{parameters['height']}мм/{parameters['length']}мм"
            matches = df[df['Наименование'].str.contains(pattern, na=False)]
            
            if not matches.empty:
                product = matches.iloc[0]
                return f"{product['Артикул']} - {product['Наименование']}"
    
    return "Соответствие не найдено"

def check_meteor_article(article):
    """Проверка артикула METEOR в базе данных"""
    sheets = st.session_state.sheets
    
    for sheet_name, df in sheets.items():
        if article in df['Артикул'].astype(str).values:
            product = df[df['Артикул'].astype(str) == article].iloc[0]
            return f"✅ Найден: {product['Наименование']}"
    
    return "❌ Не найден в базе"

def display_processed_data(processed_df, data_type):
    """Отображение обработанных данных"""
    st.subheader("📋 Обработанные данные")
    
    if data_type == "METEOR":
        st.dataframe(processed_df, use_container_width=True)
        
        # Статистика
        total_articles = len(processed_df)
        found_articles = len(processed_df[processed_df['Статус'].str.startswith('✅')])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего артикулов", total_articles)
        with col2:
            st.metric("Найдено в базе", found_articles)
            
    else:  # Competitor
        st.dataframe(processed_df, use_container_width=True)
        
        # Статистика для конкурентов
        total_products = len(processed_df)
        recognized_products = len(processed_df[processed_df['Параметры'].notna()])
        mapped_products = len(processed_df[processed_df['Соответствие METEOR'] != "Соответствие не найдено"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего продуктов", total_products)
        with col2:
            st.metric("Распознано", recognized_products)
        with col3:
            st.metric("Сопоставлено", mapped_products)
    
    # Кнопка импорта
    if st.button("✅ Импортировать в систему", type="primary", use_container_width=True):
        import_to_system(processed_df, data_type)
        st.success("✅ Данные успешно импортированы!")

def import_to_system(processed_df, data_type):
    """Импорт данных в систему"""
    if data_type == "METEOR":
        import_meteor_articles(processed_df)
    else:
        import_competitor_articles(processed_df)

def import_meteor_articles(df):
    """Импорт артикулов METEOR в матрицу"""
    imported_count = 0
    
    for _, row in df.iterrows():
        if row['Статус'].startswith('✅'):
            # Поиск артикула в базе для определения параметров
            article = row['Артикул']
            quantity = row['Количество']
            
            # Поиск в каких листах есть этот артикул
            sheets = st.session_state.sheets
            for sheet_name, sheet_df in sheets.items():
                if article in sheet_df['Артикул'].astype(str).values:
                    product = sheet_df[sheet_df['Артикул'].astype(str) == article].iloc[0]
                    
                    # Добавление в матрицу
                    key = (sheet_name, article)
                    current_value = st.session_state.entry_values.get(key, "")
                    
                    if current_value:
                        new_value = f"{current_value}+{quantity}"
                    else:
                        new_value = str(quantity)
                    
                    st.session_state.entry_values[key] = new_value
                    imported_count += 1
                    break
    
    st.info(f"📥 Импортировано {imported_count} позиций в матрицу")

def manual_column_selection(df):
    """Ручной выбор столбцов для METEOR"""
    st.subheader("🔧 Ручной выбор столбцов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        art_col_manual = st.selectbox("Столбец с артикулами:", df.columns, key="art_manual")
    
    with col2:
        qty_col_manual = st.selectbox("Столбец с количествами:", df.columns, key="qty_manual")
    
    if st.button("Применить выбор", key="apply_manual"):
        processed_df = process_meteor_data(df, art_col_manual, qty_col_manual)
        if not processed_df.empty:
            display_processed_data(processed_df, "METEOR")

def manual_competitor_selection(df):
    """Ручной выбор столбцов для конкурентов"""
    st.subheader("🔧 Ручной выбор столбцов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name_col_manual = st.selectbox("Столбец с наименованиями:", df.columns, key="name_manual")
    
    with col2:
        qty_col_manual = st.selectbox("Столбец с количествами:", df.columns, key="qty_manual_comp")
    
    if st.button("Применить выбор", key="apply_manual_comp"):
        processed_df = process_competitor_data(df, name_col_manual, qty_col_manual)
        if not processed_df.empty:
            display_processed_data(processed_df, "Competitor")

if __name__ == "__main__":
    main()