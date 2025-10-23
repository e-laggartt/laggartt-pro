# utils/create_test_data.py
import pandas as pd
import os

def create_test_matrix_data():
    """Создает тестовые данные для матрицы радиаторов"""
    
    # Создаем директорию data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Создаем Excel файл с несколькими листами
    with pd.ExcelWriter('data/Матрица.xlsx', engine='openpyxl') as writer:
        
        # Создаем данные для разных комбинаций подключения и типа
        combinations = [
            ("VK-правое", "10"),
            ("VK-правое", "11"), 
            ("VK-правое", "20"),
            ("VK-правое", "21"),
            ("VK-правое", "22"),
            ("VK-правое", "30"),
            ("VK-правое", "33"),
            ("VK-левое", "10"),
            ("VK-левое", "11"),
            ("VK-левое", "30"),
            ("VK-левое", "33"),
            ("K-боковое", "10"),
            ("K-боковое", "11"),
            ("K-боковое", "20"),
            ("K-боковое", "21"),
            ("K-боковое", "22"),
            ("K-боковое", "30"),
            ("K-боковое", "33"),
        ]
        
        heights = [300, 400, 500, 600, 900]
        lengths = list(range(400, 2100, 100))
        
        for connection, rad_type in combinations:
            sheet_data = []
            
            for height in heights:
                for length in lengths:
                    # Создаем тестовые данные для каждого размера
                    articul = f"R{rad_type}{height}{length}"
                    name = f"Радиатор METEOR тип {rad_type}/{height}мм/{length}мм"
                    power = length * 0.5 + height * 0.3  # Пример расчета мощности
                    weight = length * 0.01 + height * 0.005  # Пример расчета веса
                    volume = length * height * 0.000001  # Пример расчета объема
                    price = length * 2 + height * 1  # Пример расчета цены
                    
                    sheet_data.append({
                        'Артикул': articul,
                        'Наименование': name,
                        'Мощность, Вт': round(power, 1),
                        'Вес, кг': round(weight, 2),
                        'Объем, м3': round(volume, 4),
                        'Цена, руб': round(price, 2)
                    })
            
            df = pd.DataFrame(sheet_data)
            sheet_name = f"{connection} {rad_type}"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print("Тестовые данные созданы успешно!")

if __name__ == "__main__":
    create_test_matrix_data()