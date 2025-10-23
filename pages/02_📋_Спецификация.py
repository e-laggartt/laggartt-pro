# pages/02_📋_Спецификация.py
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Спецификация - RadiaTool Pro", 
    page_icon="📋",
    layout="wide"
)

def main():
    st.title("📋 Спецификация")
    st.markdown("---")
    
    # Проверка наличия данных в session_state
    if 'entry_values' not in st.session_state or not st.session_state.entry_values:
        st.warning("❌ Матрица радиаторов пуста. Заполните данные на главной странице.")
        if st.button("➡️ Перейти к матрице"):
            # Используем правильный путь к главной странице
            st.switch_page("pages/Главная.py")
        return
    
    # Создаем демо-спецификацию для тестирования
    spec_data = create_demo_specification()
    
    if spec_data.empty:
        st.warning("❌ Нет данных для отображения в спецификации.")
        return
    
    # Отображение спецификации
    st.subheader("Текущая спецификация")
    
    # Редактируемая таблица
    edited_df = st.data_editor(
        spec_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Артикул": st.column_config.TextColumn(width="medium"),
            "Наименование": st.column_config.TextColumn(width="large"),
            "Количество": st.column_config.NumberColumn(width="small", min_value=0),
            "Цена": st.column_config.NumberColumn(format="%.2f ₽"),
            "Сумма": st.column_config.NumberColumn(format="%.2f ₽"),
            "Тип": st.column_config.SelectboxColumn(
                options=["Радиатор", "Кронштейн"],
                width="small"
            )
        },
        disabled=["Артикул", "Наименование"]
    )
    
    # Сохранение изменений
    if not edited_df.equals(spec_data):
        st.session_state.spec_data = edited_df
        st.success("✅ Изменения сохранены!")
    
    # Кнопки управления
    st.markdown("---")
    st.subheader("🚀 Управление спецификацией")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Обновить", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📥 Excel", use_container_width=True):
            export_specification_to_excel(edited_df)
    
    with col3:
        if st.button("📄 CSV", use_container_width=True):
            export_specification_to_csv(edited_df)
    
    with col4:
        if st.button("🗑️ Очистить", type="secondary", use_container_width=True):
            st.session_state.entry_values = {}
            st.session_state.spec_data = pd.DataFrame()
            st.rerun()
    
    # Итоги
    st.markdown("---")
    show_totals(edited_df)
    
    # Быстрое копирование
    st.markdown("---")
    show_quick_copy(edited_df)

def create_demo_specification():
    """Создание демо-спецификации на основе заполненных данных"""
    spec_rows = []
    
    # Обрабатываем заполненные данные из матрицы
    if 'entry_values' in st.session_state:
        for key, value in st.session_state.entry_values.items():
            if value:  # Если есть значение
                sheet_name, art = key
                quantity = parse_quantity(value)
                
                if quantity > 0:
                    # Создаем демо-данные для радиатора
                    spec_rows.append({
                        "Артикул": art,
                        "Наименование": f"Радиатор {sheet_name}",
                        "Количество": quantity,
                        "Цена": 15000.0,
                        "Сумма": quantity * 15000.0,
                        "Тип": "Радиатор"
                    })
    
    # Добавляем демо-кронштейны если выбран тип с кронштейнами
    if st.session_state.get('bracket_type', 'Без кронштейнов') != "Без кронштейнов":
        spec_rows.append({
            "Артикул": "К9.2L",
            "Наименование": "Кронштейн настенный левый",
            "Количество": 2,
            "Цена": 500.0,
            "Сумма": 1000.0,
            "Тип": "Кронштейн"
        })
        spec_rows.append({
            "Артикул": "К9.2R", 
            "Наименование": "Кронштейн настенный правый",
            "Количество": 2,
            "Цена": 500.0,
            "Сумма": 1000.0,
            "Тип": "Кронштейн"
        })
    
    return pd.DataFrame(spec_rows)

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

def show_totals(df):
    """Отображение итогов"""
    if df.empty:
        return
    
    # Основные итоги
    total_qty = df['Количество'].sum()
    total_sum = df['Сумма'].sum()
    
    # Разделение на радиаторы и кронштейны
    rad_df = df[df['Тип'] == 'Радиатор']
    br_df = df[df['Тип'] == 'Кронштейн']
    
    rad_qty = rad_df['Количество'].sum()
    rad_sum = rad_df['Сумма'].sum()
    br_qty = br_df['Количество'].sum() 
    br_sum = br_df['Сумма'].sum()
    
    # Применение скидок
    discounts = st.session_state.get('discounts', {"radiators": 0, "brackets": 0})
    rad_discounted = rad_sum * (1 - discounts['radiators'] / 100)
    br_discounted = br_sum * (1 - discounts['brackets'] / 100)
    total_discounted = rad_discounted + br_discounted
    
    # Отображение итогов
    st.subheader("📊 Итоги")
    
    # Финансовые итоги
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Общее количество", f"{total_qty:.0f} шт")
        st.metric("Радиаторы", f"{rad_qty:.0f} шт")
        st.metric("Кронштейны", f"{br_qty:.0f} шт")
    
    with col2:
        st.metric("Общая стоимость", f"{total_sum:,.2f} ₽")
        st.metric("Стоимость радиаторов", f"{rad_sum:,.2f} ₽")
        st.metric("Стоимость кронштейнов", f"{br_sum:,.2f} ₽")
    
    with col3:
        st.metric("Скидка радиаторы", f"-{discounts['radiators']}%")
        st.metric("Скидка кронштейны", f"-{discounts['brackets']}%")
        st.metric("Итого со скидкой", f"{total_discounted:,.2f} ₽")
    
    with col4:
        st.metric("Позиций в спецификации", len(df))
        st.metric("Средняя цена", f"{total_sum/total_qty:,.2f} ₽" if total_qty > 0 else "0 ₽")

def show_quick_copy(df):
    """Быстрое копирование в буфер"""
    st.subheader("📋 Быстрое копирование")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Скопировать артикулы", use_container_width=True):
            articles = "\n".join(df['Артикул'].astype(str))
            st.session_state.copied_articles = articles
            st.success("✅ Артикулы скопированы в буфер!")
    
    with col2:
        if st.button("📋 Скопировать количества", use_container_width=True):
            quantities = "\n".join(df['Количество'].astype(str))
            st.session_state.copied_quantities = quantities
            st.success("✅ Количества скопированы в буфер!")
    
    # Показать скопированные данные
    if 'copied_articles' in st.session_state:
        with st.expander("📋 Просмотреть скопированные артикулы"):
            st.text_area("Артикулы", st.session_state.copied_articles, height=150, key="articles_area")
    
    if 'copied_quantities' in st.session_state:
        with st.expander("📋 Просмотреть скопированные количества"):
            st.text_area("Количества", st.session_state.copied_quantities, height=150, key="quantities_area")

def export_specification_to_excel(df):
    """Экспорт спецификации в Excel"""
    try:
        from io import BytesIO
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Спецификация', index=False)
            
            # Автоподбор ширины столбцов
            workbook = writer.book
            worksheet = writer.sheets['Спецификация']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        st.success("✅ Файл подготовлен для скачивания")
        st.download_button(
            label="📥 Скачать Excel файл",
            data=output.getvalue(),
            file_name=f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_download"
        )
    except Exception as e:
        st.error(f"❌ Ошибка экспорта в Excel: {e}")

def export_specification_to_csv(df):
    """Экспорт спецификации в CSV"""
    try:
        # CSV с разделителем точка с запятой и кодировкой UTF-8-sig
        output = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        
        st.success("✅ CSV файл подготовлен для скачивания")
        st.download_button(
            label="📥 Скачать CSV файл",
            data=output.encode('utf-8-sig'),
            file_name=f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            key="csv_download"
        )
    except Exception as e:
        st.error(f"❌ Ошибка экспорта в CSV: {e}")

if __name__ == "__main__":
    main()