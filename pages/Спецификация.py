# pages/02_📋_Спецификация.py
import streamlit as st
import pandas as pd
from utils.session_manager import get_specification_data
from utils.exporter import export_to_excel, export_to_csv

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
            st.switch_page("pages/Главная.py")
        return
    
    # Формирование спецификации
    spec_data = get_specification_data()
    
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
        disabled=["Артикул", "Наименование", "Мощность, Вт", "Вес, кг", "Объем, м3"]
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
            st.session_state.spec_data = get_specification_data()
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

def show_totals(df):
    """Отображение итогов согласно ТЗ"""
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
    discounts = st.session_state.discounts
    rad_discounted = rad_sum * (1 - discounts['radiators'] / 100)
    br_discounted = br_sum * (1 - discounts['brackets'] / 100)
    total_discounted = rad_discounted + br_discounted
    
    # Технические параметры
    total_power = (rad_df['Мощность, Вт'] * rad_df['Количество']).sum()
    total_weight = (df['Вес, кг'] * df['Количество']).sum()
    total_volume = (df['Объем, м3'] * df['Количество']).sum()
    
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
        # Автоформатирование технических параметров
        power_text = format_power(total_power)
        weight_text = format_weight(total_weight)
        volume_text = format_volume(total_volume)
        
        st.metric("Суммарная мощность", power_text)
        st.metric("Общий вес", weight_text)
        st.metric("Общий объем", volume_text)

def format_power(watts):
    """Автоформатирование мощности согласно ТЗ"""
    if watts >= 1000000:
        return f"{watts/1000000:.2f} МВт"
    elif watts >= 1000:
        return f"{watts/1000:.2f} кВт"
    else:
        return f"{watts:.0f} Вт"

def format_weight(kg):
    """Автоформатирование веса согласно ТЗ"""
    if kg >= 1000:
        return f"{kg/1000:.2f} т"
    else:
        return f"{kg:.1f} кг"

def format_volume(m3):
    """Форматирование объема"""
    return f"{m3:.3f} м³"

def show_quick_copy(df):
    """Быстрое копирование в буфер согласно ТЗ"""
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
        from utils.exporter import export_to_excel
        
        file_data, filename = export_to_excel(df)
        
        if file_data:
            st.success("✅ Файл подготовлен для скачивания")
            st.download_button(
                label="📥 Скачать Excel файл",
                data=file_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="excel_download"
            )
    except Exception as e:
        st.error(f"❌ Ошибка экспорта в Excel: {e}")

def export_specification_to_csv(df):
    """Экспорт спецификации в CSV"""
    try:
        from utils.exporter import export_to_csv
        
        file_data, filename = export_to_csv(df)
        
        if file_data:
            st.success("✅ CSV файл подготовлен для скачивания")
            st.download_button(
                label="📥 Скачать CSV файл",
                data=file_data,
                file_name=filename,
                mime="text/csv",
                key="csv_download"
            )
    except Exception as e:
        st.error(f"❌ Ошибка экспорта в CSV: {e}")

if __name__ == "__main__":
    main()