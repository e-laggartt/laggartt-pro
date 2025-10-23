# pages/01_🏠_Главная.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Главная - RadiaTool Pro",
    page_icon="🏠",
    layout="wide"
)

def parse_quantity(value):
    """Парсинг количеств с поддержкой формул"""
    if not value:
        return 0
    
    value = str(value).strip()
    
    # Удаление лишних +
    while value.startswith('+'):
        value = value[1:]
    while value.endswith('+'):
        value = value[:-1]
        
    if not value:
        return 0
    
    # Суммирование частей
    try:
        parts = value.split('+')
        total = sum(int(round(float(part))) for part in parts if part.strip())
        return total
    except (ValueError, TypeError):
        return 0

def load_radiator_data():
    """Загрузка реальных данных из Excel файла"""
    try:
        file_path = "data/Матрица.xlsx"
        if os.path.exists(file_path):
            # Чтение всех листов Excel
            sheets_dict = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
            
            # Обработка данных
            processed_sheets = {}
            for sheet_name, df in sheets_dict.items():
                # Приведение артикулов к строковому типу
                if 'Артикул' in df.columns:
                    df['Артикул'] = df['Артикул'].astype(str)
                
                # Заполнение пропущенных числовых значений
                numeric_columns = ['Мощность, Вт', 'Вес, кг', 'Объем, м3', 'Цена, руб']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                processed_sheets[sheet_name] = df
            
            return processed_sheets
        else:
            st.error(f"❌ Файл {file_path} не найден")
            return {}
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")
        return {}

def find_radiator_by_size(df, height, length):
    """Поиск радиатора по высоте и длине в реальных данных"""
    try:
        # Паттерн для поиска в наименовании
        pattern = f"/{height}мм/{length}мм"
        
        # Ищем в столбце 'Наименование'
        for _, row in df.iterrows():
            name = str(row.get('Наименование', ''))
            if pattern in name:
                return row
        
        return None
        
    except Exception as e:
        st.error(f"Ошибка поиска радиатора: {e}")
        return None

def main():
    st.title("🏠 Матрица радиаторов")
    
    # Инициализация session_state
    if 'entry_values' not in st.session_state:
        st.session_state.entry_values = {}
    if 'connection' not in st.session_state:
        st.session_state.connection = "VK-правое"
    if 'radiator_type' not in st.session_state:
        st.session_state.radiator_type = "10"
    if 'bracket_type' not in st.session_state:
        st.session_state.bracket_type = "Настенные кронштейны"
    if 'discounts' not in st.session_state:
        st.session_state.discounts = {"radiators": 0, "brackets": 0}
    if 'sheets' not in st.session_state:
        st.session_state.sheets = load_radiator_data()
    
    sheets = st.session_state.sheets
    
    # Проверка загрузки данных
    if not sheets:
        st.error("❌ Не удалось загрузить данные радиаторов.")
        st.info("Убедитесь, что файл data/Матрица.xlsx существует и содержит данные.")
        return
    
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
                min_value=0,
                max_value=100,
                value=int(st.session_state.discounts["radiators"]),
                step=1,
                key="rad_discount_input"
            )
        with col2:
            br_discount = st.number_input(
                "Кронштейны, %",
                min_value=0,
                max_value=100,
                value=int(st.session_state.discounts["brackets"]),
                step=1,
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
            value=True,
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
        
        # Информация о данных
        st.markdown("---")
        st.subheader("📊 Информация")
        st.write(f"Загружено листов: {len(sheets)}")
        total_products = sum(len(df) for df in sheets.values())
        st.write(f"Всего радиаторов: {total_products}")
    
    # Основная область - матрица радиаторов
    st.header(f"📊 Матрица: {connection} {radiator_type}")
    
    sheet_name = f"{connection} {radiator_type}"
    if sheet_name not in sheets:
        st.error(f"❌ Лист '{sheet_name}' не найден в данных")
        st.info("📋 Доступные листы в данных:")
        for available_sheet in sheets.keys():
            st.write(f"- {available_sheet}")
        
        # Используем первый доступный лист для демонстрации
        if sheets:
            first_sheet = list(sheets.keys())[0]
            st.info(f"🔧 Используется лист: {first_sheet}")
            df = sheets[first_sheet]
        else:
            return
    else:
        df = sheets[sheet_name]
    
    # Размеры матрицы согласно ТЗ
    lengths = list(range(400, 2100, 100))  # 400-2000 с шагом 100
    heights = [300, 400, 500, 600, 900]
    
    # Создание матрицы
    st.markdown("#### Длина радиаторов, мм →")
    
    # Заголовки столбцов (высоты)
    cols = st.columns(len(heights) + 1)
    with cols[0]:
        st.markdown("**Высота<br>радиаторов, мм**", unsafe_allow_html=True)
    
    for j, height in enumerate(heights):
        with cols[j + 1]:
            st.markdown(f"**{height}**")
    
    # Строки матрицы
    total_filled = 0
    total_quantity = 0
    
    for i, length in enumerate(lengths):
        cols = st.columns(len(heights) + 1)
        
        # Заголовок строки (длина)
        with cols[0]:
            st.markdown(f"**{length}**")
        
        # Ячейки матрицы
        for j, height in enumerate(heights):
            with cols[j + 1]:
                # Поиск радиатора по размерам в реальных данных
                product = find_radiator_by_size(df, height, length)
                
                if product is not None:
                    art = str(product['Артикул'])
                    key = (sheet_name, art)
                    
                    current_val = st.session_state.entry_values.get(key, "")
                    
                    # Поле ввода с валидацией
                    new_val = st.text_input(
                        "",
                        value=current_val,
                        key=f"matrix_{length}_{height}_{i}_{j}",
                        label_visibility="collapsed",
                        placeholder="0"
                    )
                    
                    # Валидация ввода
                    if new_val and not all(c in '0123456789+' for c in new_val):
                        st.error("❌ Только цифры и +")
                        new_val = current_val
                    
                    # Обновление значения
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
                        
                        # Создаем всплывающую подсказку
                        with st.popover("ℹ️", use_container_width=True):
                            st.markdown(f"**{product.get('Наименование', 'N/A')}**")
                            st.markdown("---")
                            st.markdown(f"**Артикул:** {art}")
                            st.markdown(f"**Мощность:** {power} Вт")
                            st.markdown(f"**Вес:** {weight} кг")
                            st.markdown(f"**Объем:** {volume} м³")
                            st.markdown(f"**Цена:** {price} ₽")
                            
                            if new_val and parse_quantity(new_val) > 0:
                                qty = parse_quantity(new_val)
                                st.markdown(f"**Выбрано:** {qty} шт")
                                st.markdown(f"**Сумма:** {qty * float(price or 0):.2f} ₽")
                
                else:
                    # Если радиатор не найден в реальных данных
                    st.markdown("—")
                    if st.session_state.show_tooltips:
                        st.markdown("", help="Радиатор не найден в базе данных")
    
    # Статистика и навигация
    st.markdown("---")
    
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
        
        # Инструкция
        with st.expander("📝 Как работать с матрицей?"):
            st.markdown("""
            1. **Выберите параметры** в боковой панели
            2. **Заполните матрицу** - вводите количества в ячейки
            3. **Используйте +** для суммирования: `1+2+3`
            4. **Перейдите к спецификации** для просмотра результатов
            """)

if __name__ == "__main__":
    main()