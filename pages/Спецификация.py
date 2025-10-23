# pages/02_📋_Спецификация.py
import streamlit as st
import pandas as pd
from utils.calculator import parse_quantity, calculate_wall_brackets

st.set_page_config(
    page_title="Спецификация - RadiaTool Pro", 
    page_icon="📋",
    layout="wide"
)

def main():
    st.title("📋 Спецификация")
    st.markdown("---")
    
    # Проверка наличия данных
    if not st.session_state.get('entry_values'):
        st.warning("❌ Матрица радиаторов пуста. Заполните данные на главной странице.")
        if st.button("➡️ Перейти к матрице"):
            st.switch_page("app.py")
        return
    
    # Формирование спецификации
    spec_data = generate_specification()
    
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
            "Количество": st.column_config.NumberColumn(width="small"),
            "Цена": st.column_config.NumberColumn(format="%.2f ₽"),
            "Сумма": st.column_config.NumberColumn(format="%.2f ₽")
        }
    )
    
    # Кнопки управления
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Обновить спецификацию", use_container_width=True):
            st.session_state.spec_data = edited_df
            st.rerun()
    
    with col2:
        if st.button("📥 Экспорт в Excel", use_container_width=True):
            export_to_excel(edited_df)
    
    with col3:
        if st.button("🗑️ Очистить спецификацию", type="secondary", use_container_width=True):
            st.session_state.spec_data = pd.DataFrame()
            st.session_state.entry_values = {}
            st.rerun()
    
    # Итоги
    st.markdown("---")
    show_totals(edited_df)

def generate_specification():
    """Формирование спецификации на основе заполненной матрицы"""
    
    # Временные данные (заглушка)
    spec_rows = []
    
    # Обработка заполненных ячеек матрицы
    for key, value in st.session_state.entry_values.items():
        if value and parse_quantity(value) > 0:
            height, length = key.split('_')
            qty = parse_quantity(value)
            
            # Генерация артикула и наименования (заглушка)
            art = f"VK-{st.session_state.radiator_type}-{height}-{length}"
            name = f"Радиатор {st.session_state.connection} тип {st.session_state.radiator_type} {height}x{length}"
            price = 15000  # Заглушка
            
            spec_rows.append({
                "Артикул": art,
                "Наименование": name,
                "Количество": qty,
                "Цена": price,
                "Сумма": qty * price
            })
    
    # Добавление кронштейнов
    if st.session_state.bracket_type != "Без":
        bracket_rows = generate_brackets_spec()
        spec_rows.extend(bracket_rows)
    
    return pd.DataFrame(spec_rows)

def generate_brackets_spec():
    """Генерация спецификации кронштейнов"""
    bracket_rows = []
    
    # Расчет кронштейнов для каждого радиатора
    for key, value in st.session_state.entry_values.items():
        if value and parse_quantity(value) > 0:
            height, length = map(int, key.split('_'))
            qty = parse_quantity(value)
            
            if st.session_state.bracket_type == "Настенные":
                brackets = calculate_wall_brackets(
                    st.session_state.radiator_type,
                    length, height, qty
                )
                
                for art, br_qty in brackets:
                    price = 500  # Заглушка
                    bracket_rows.append({
                        "Артикул": art,
                        "Наименование": f"Кронштейн настенный {art}",
                        "Количество": br_qty,
                        "Цена": price,
                        "Сумма": br_qty * price
                    })
    
    return bracket_rows

def show_totals(df):
    """Отображение итогов"""
    if df.empty:
        return
    
    total_qty = df['Количество'].sum()
    total_sum = df['Сумма'].sum()
    
    # Применение скидок
    discounts = st.session_state.discounts
    rad_sum = df[~df['Наименование'].str.contains('Кронштейн', na=False)]['Сумма'].sum()
    br_sum = df[df['Наименование'].str.contains('Кронштейн', na=False)]['Сумма'].sum()
    
    rad_discounted = rad_sum * (1 - discounts['radiators'] / 100)
    br_discounted = br_sum * (1 - discounts['brackets'] / 100)
    total_discounted = rad_discounted + br_discounted
    
    # Отображение итогов
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Общее количество", f"{total_qty:.0f} шт")
    
    with col2:
        st.metric("Общая стоимость", f"{total_sum:,.2f} ₽")
    
    with col3:
        st.metric("Скидка радиаторы", f"-{discounts['radiators']}%")
    
    with col4:
        st.metric("Итого со скидкой", f"{total_discounted:,.2f} ₽")

def export_to_excel(df):
    """Экспорт в Excel"""
    try:
        from io import BytesIO
        import openpyxl
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Спецификация', index=False)
            
            # Настройка форматирования
            workbook = writer.book
            worksheet = writer.sheets['Спецификация']
            
            # Автоподбор ширины столбцов
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        st.success("✅ Файл подготовлен для скачивания")
        st.download_button(
            label="📥 Скачать Excel файл",
            data=output.getvalue(),
            file_name=f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"❌ Ошибка экспорта: {e}")

if __name__ == "__main__":
    main()