# pages/04_ℹ️_Информация.py
import streamlit as st

st.set_page_config(
    page_title="Информация - RadiaTool Pro",
    page_icon="ℹ️",
    layout="wide"
)

def main():
    st.title("ℹ️ Информация и поддержка")
    st.markdown("---")
    
    # Вкладки
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Инструкция", 
        "💰 Прайс-листы", 
        "📄 Документация",
        "🛠️ Поддержка"
    ])
    
    with tab1:
        show_instructions()
    
    with tab2:
        show_price_lists()
    
    with tab3:
        show_documentation()
    
    with tab4:
        show_support()

def show_instructions():
    """Инструкция по использованию"""
    
    st.header("📖 Инструкция по использованию")
    
    st.markdown("""
    ### 🚀 Быстрый старт
    
    1. **Настройте параметры** в боковой панели:
       - Выберите тип подключения
       - Выберите тип радиатора  
       - Укажите тип крепления
       - Задайте скидки (если нужно)
    
    2. **Заполните матрицу** радиаторов:
       - Вводите количества в соответствующие ячейки
       - Поддерживается ввод формул: `1+2+3`
       - Только цифры и знак `+`
    
    3. **Просмотрите спецификацию**:
       - Автоматическое формирование позиций
       - Расчет кронштейнов
       - Итоговые суммы со скидками
    
    4. **Экспортируйте результаты**:
       - Excel файл с форматированием
       - CSV для других систем
    """)
    
    # Видео-гайды (заглушки)
    st.subheader("🎥 Видео-гайды")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🎬 Базовое использование", use_container_width=True)
    
    with col2:
        st.button("⚡ Расширенные возможности", use_container_width=True)
    
    with col3:
        st.button("🔧 Решение проблем", use_container_width=True)

def show_price_lists():
    """Прайс-листы"""
    
    st.header("💰 Прайс-листы")
    
    st.info("""
    **Актуальные прайс-листы METEOR:**
    - Обновляются ежеквартально
    - Включают все типы радиаторов и комплектующих
    """)
    
    # Кнопки загрузки прайс-листов
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Радиаторы VK",
            data="Заглушка для прайс-листа",
            file_name="METEOR_радиаторы_VK_2024.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        st.download_button(
            label="📥 Радиаторы K",
            data="Заглушка для прайс-листа", 
            file_name="METEOR_радиаторы_K_2024.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col3:
        st.download_button(
            label="📥 Кронштейны",
            data="Заглушка для прайс-листа",
            file_name="METEOR_кронштейны_2024.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.markdown("---")
    st.subheader("📅 График обновления цен")
    
    st.write("""
    | Период | Дата обновления | Статус |
    |--------|----------------|--------|
    | Q4 2024 | 01.12.2024 | 🔄 Актуальный |
    | Q1 2025 | 01.03.2025 | ⏳ Планируется |
    """)

def show_documentation():
    """Техническая документация"""
    
    st.header("📄 Техническая документация")
    
    # Сертификаты
    st.subheader("📑 Сертификаты и паспорта")
    
    doc_col1, doc_col2, doc_col3 = st.columns(3)
    
    with doc_col1:
        st.button("📄 Сертификат соответствия", use_container_width=True)
    
    with doc_col2:
        st.button("📄 Паспорта изделий", use_container_width=True)
    
    with doc_col3:
        st.button("📄 Технические условия", use_container_width=True)
    
    # Формуляры
    st.subheader("📋 Формуляры для проектов")
    
    form_col1, form_col2 = st.columns(2)
    
    with form_col1:
        st.button("🏗️ Формуляр для проектировщиков", use_container_width=True)
    
    with form_col2:
        st.button("📊 Технические спецификации", use_container_width=True)
    
    # Расчетные инструменты
    st.subheader("🛠️ Расчетные инструменты")
    
    if st.button("🧮 Калькулятор мощностей"):
        st.info("📎 Загрузка калькулятора...")

def show_support():
    """Техническая поддержка"""
    
    st.header("🛠️ Техническая поддержка")
    
    st.success("""
    **Мы всегда готовы помочь!**
    
    По всем вопросам работы программы обращайтесь:
    """)
    
    # Контакты
    st.subheader("📞 Контакты")
    
    st.write("""
    **📧 Email:** mt@laggartt.ru
    **🌐 Website:** www.laggartt.ru
    **💬 Telegram:** @laggartt_support
    """)
    
    # Форма обратной связи
    st.subheader("📝 Обратная связь")
    
    with st.form("feedback_form"):
        name = st.text_input("Ваше имя")
        email = st.text_input("Email для ответа")
        topic = st.selectbox("Тема обращения", [
            "Техническая проблема",
            "Предложение по улучшению", 
            "Вопрос по функционалу",
            "Другое"
        ])
        message = st.text_area("Сообщение", height=150)
        
        submitted = st.form_submit_button("📤 Отправить обращение")
        
        if submitted:
            if name and email and message:
                st.success("✅ Ваше сообщение отправлено! Ответим в течение 24 часов.")
            else:
                st.error("❌ Заполните все обязательные поля")
    
    # FAQ
    st.subheader("❓ Часто задаваемые вопросы")
    
    with st.expander("Как вводить несколько радиаторов в одну ячейку?"):
        st.write("Используйте знак + между количествами: `1+2+3`")
    
    with st.expander("Не загружается файл Excel"):
        st.write("Проверьте, что файл не открыт в другой программе и имеет расширение .xlsx или .xls")
    
    with st.expander("Как сбросить все данные?"):
        st.write("Используйте кнопку 'Сброс' в боковой панели")

if __name__ == "__main__":
    main()