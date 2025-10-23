# utils/exporter.py
import pandas as pd
import streamlit as st

def export_to_excel(df, filename=None):
    """Экспорт DataFrame в Excel с форматированием"""
    
    if filename is None:
        filename = f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    try:
        from io import BytesIO
        import openpyxl
        from openpyxl.styles import Font, Alignment, Border, Side
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Спецификация', index=False)
            
            # Настройка форматирования
            workbook = writer.book
            worksheet = writer.sheets['Спецификация']
            
            # Стили
            header_font = Font(bold=True, size=12)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'), 
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Форматирование заголовков
            for cell in worksheet[1]:
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')
                cell.border = border
            
            # Форматирование данных
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
                for cell in row:
                    cell.border = border
                    if cell.column in [4, 5]:  # Цена и Сумма
                        cell.number_format = '#,##0.00'
            
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
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return output.getvalue(), filename
        
    except Exception as e:
        st.error(f"❌ Ошибка экспорта: {e}")
        return None, None

def export_to_csv(df, filename=None):
    """Экспорт в CSV"""
    
    if filename is None:
        filename = f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"
    
    try:
        output = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        return output.encode('utf-8-sig'), filename
        
    except Exception as e:
        st.error(f"❌ Ошибка экспорта CSV: {e}")
        return None, None