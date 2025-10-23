# pages/03_📊_Импорт_данных.py
import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Импорт данных - RadiaTool Pro",
    page_icon="📊", 
    layout="wide"
)

def main():
    st.title("📊 Импорт данных")
    st.markdown("---")
    
    # Выбор типа импорта
    import_type = st.radio(
        "Тип импорта:",
        ["METEOR спецификация", "Другие производители"],
        horizontal=True
    )
    
    if import_type == "METEOR спецификация":
        import_meteor_spec()
    else:
        import_other_manufacturers()

def import_meteor_spec():
    """Импорт спецификаций METEOR"""
    
    st.subheader("Импорт из METEOR")
    
    uploaded_file = st.file_uploader(
        "Загрузите файл спецификации",
        type=['xlsx', 'xls', 'csv'],
        help="Поддерживаются форматы: Excel (.xlsx, .xls), CSV"
    )
    
    if uploaded_file is not None:
        try:
            # Чтение файла
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Файл загружен: {uploaded_file.name}")
            st.write("Предпросмотр данных:")
            st.dataframe(df.head(), use_container_width=True)
            
            # Автораспознавание столбцов
            art_col, qty_col = detect_columns(df)
            
            if art_col and qty_col:
                st.info(f"📊 Распознано: Артикул - '{art_col}', Количество - '{qty_col}'")
                
                # Обработка данных
                processed_df = process_imported_data(df, art_col, qty_col)
                
                if not processed_df.empty:
                    st.subheader("Обработанные данные")
                    st.dataframe(processed_df, use_container_width=True)
                    
                    # Импорт в систему
                    if st.button("✅ Импортировать в спецификацию", type="primary"):
                        import_to_specification(processed_df)
                        st.success("✅ Данные успешно импортированы!")
                        
            else:
                st.error("❌ Не удалось автоматически определить столбцы")
                manual_column_selection(df)
                
        except Exception as e:
            st.error(f"❌ Ошибка загрузки файла: {e}")

def detect_columns(df):
    """Автораспознавание столбцов"""
    art_col, qty_col = None, None
    
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['артикул', 'art', 'код', 'code']):
            art_col = col
        elif any(keyword in col_lower for keyword in ['кол-во', 'количество', 'qty', 'quantity']):
            qty_col = col
    
    return art_col, qty_col

def process_imported_data(df, art_col, qty_col):
    """Обработка импортированных данных"""
    try:
        # Базовая очистка
        processed_df = df[[art_col, qty_col]].copy()
        processed_df.columns = ['Артикул', 'Количество']
        
        # Удаление пустых строк
        processed_df = processed_df.dropna()
        
        # Преобразование количеств
        processed_df['Количество'] = pd.to_numeric(processed_df['Количество'], errors='coerce')
        processed_df = processed_df.dropna(subset=['Количество'])
        
        # Суммирование одинаковых артикулов
        processed_df = processed_df.groupby('Артикул', as_index=False)['Количество'].sum()
        
        return processed_df
        
    except Exception as e:
        st.error(f"❌ Ошибка обработки данных: {e}")
        return pd.DataFrame()

def import_to_specification(processed_df):
    """Импорт данных в текущую спецификацию"""
    # Здесь будет логика преобразования артикулов в параметры матрицы
    st.info("🔄 Функция импорта в разработке...")

def manual_column_selection(df):
    """Ручной выбор столбцов"""
    st.subheader("Ручной выбор столбцов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        art_col_manual = st.selectbox("Столбец с артикулами:", df.columns)
    
    with col2:
        qty_col_manual = st.selectbox("Столбец с количествами:", df.columns)
    
    if st.button("Применить выбор"):
        processed_df = process_imported_data(df, art_col_manual, qty_col_manual)
        if not processed_df.empty:
            st.dataframe(processed_df, use_container_width=True)

def import_other_manufacturers():
    """Импорт данных других производителей"""
    st.subheader("Импорт данных других производителей")
    
    st.info("""
    **Поддерживаемые форматы:**
    - VC 22-500-600
    - ЛК 11-504  
    - тип 10-400-1000
    """)
    
    uploaded_file = st.file_uploader(
        "Загрузите файл с наименованиями",
        type=['xlsx', 'xls', 'csv']
    )
    
    if uploaded_file:
        st.warning("⚠️ Функция в активной разработке")

if __name__ == "__main__":
    main()