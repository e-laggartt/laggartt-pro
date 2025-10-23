# utils/exporter.py
import pandas as pd
import streamlit as st
from io import BytesIO

def export_to_excel(df, filename=None):
    """Экспорт DataFrame в Excel с форматированием согласно ТЗ"""
    
    if filename is None:
        filename = f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    try:
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Лист "Спецификация"
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
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Добавление итоговой строки
            total_row = len(df) + 2
            worksheet.cell(row=total_row, column=1, value="ИТОГО:")
            worksheet.cell(row=total_row, column=4, value=df['Количество'].sum())
            worksheet.cell(row=total_row, column=6, value=df['Сумма'].sum())
        
        return output.getvalue(), filename
        
    except Exception as e:
        st.error(f"❌ Ошибка экспорта: {e}")
        return None, None

def export_to_csv(df, filename=None):
    """Экспорт в CSV согласно ТЗ"""
    
    if filename is None:
        filename = f"спецификация_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"
    
    try:
        # CSV с разделителем точка с запятой и кодировкой UTF-8-sig
        output = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        return output.encode('utf-8-sig'), filename
        
    except Exception as e:
        st.error(f"❌ Ошибка экспорта CSV: {e}")
        return None, None