import pandas as pd
import re

def parse_quantity(value):
    """
    Преобразует введенное значение в количество радиаторов.
    Обрабатывает целые числа и комбинации с плюсами.
    """
    if not value:
        return 0
    
    try:
        if isinstance(value, (int, float)):
            return int(round(float(value)))
        
        value = str(value).strip()
        
        # Удаление лишних знаков '+' в начале и конце
        while value.startswith('+'):
            value = value[1:]
        while value.endswith('+'):
            value = value[:-1]
        
        if not value:
            return 0
        
        # Разбиваем строку по знакам '+' и суммируем отдельные части
        parts = value.split('+')
        total = 0
        for part in parts:
            part = part.strip()
            if part:
                total += int(round(float(part)))
                
        return total
        
    except Exception:
        return 0

def calculate_brackets(radiator_type, length, height, bracket_type, qty=1):
    """
    Рассчитывает необходимые кронштейны для радиатора
    """
    brackets = []
    
    # Настенные кронштейны
    if bracket_type == "Настенные кронштейны":
        if radiator_type in ["10", "11"]:
            brackets.extend([("К9.2L", 2*qty), ("К9.2R", 2*qty)])
            if 1700 <= length <= 2000:
                brackets.append(("К9.3-40", 1*qty))
        
        elif radiator_type in ["20", "21", "22", "30", "33"]:
            art_map = {
                300: "К15.4300",
                400: "К15.4400", 
                500: "К15.4500",
                600: "К15.4600",
                900: "К15.4900"
            }
            if height in art_map:
                art = art_map[height]
                if 400 <= length <= 1600:
                    qty_br = 2*qty
                elif 1700 <= length <= 2000:
                    qty_br = 3*qty
                else:
                    qty_br = 0
                if qty_br:
                    brackets.append((art, qty_br))
    
    # Напольные кронштейны
    elif bracket_type == "Напольные кронштейны":
        if radiator_type in ["10", "11"]:
            art_map = {
                300: "КНС450", 
                400: "КНС450",
                500: "КНС470", 
                600: "КНС470", 
                900: "КНС4100"
            }
            main_art = art_map.get(height)
            if main_art:
                brackets.append((main_art, 2*qty))
                if 1700 <= length <= 2000:
                    brackets.append(("КНС430", 1*qty))
        
        elif radiator_type == "21":
            art_map = {
                300: "КНС650", 
                400: "КНС650",
                500: "КНС670", 
                600: "КНС670", 
                900: "КНС6100"
            }
            art = art_map.get(height)
            if art:
                if 400 <= length <= 1000:
                    qty_br = 2*qty
                elif 1100 <= length <= 1600:
                    qty_br = 3*qty
                elif 1700 <= length <= 2000:
                    qty_br = 4*qty
                else:
                    qty_br = 0
                if qty_br:
                    brackets.append((art, qty_br))
        
        elif radiator_type in ["20", "22", "30", "33"]:
            art_map = {
                300: "КНС550", 
                400: "КНС550",
                500: "КНС570", 
                600: "КНС570", 
                900: "КНС5100"
            }
            art = art_map.get(height)
            if art:
                if 400 <= length <= 1000:
                    qty_br = 2*qty
                elif 1100 <= length <= 1600:
                    qty_br = 3*qty
                elif 1700 <= length <= 2000:
                    qty_br = 4*qty
                else:
                    qty_br = 0
                if qty_br:
                    brackets.append((art, qty_br))
    
    return brackets

def format_power(power_w):
    """Форматирует мощность с автоматическим выбором единиц измерения"""
    try:
        power_w = float(power_w)
        
        if power_w >= 1_000_000:
            return f"{power_w / 1_000_000:.3f} МВт"
        elif power_w >= 1_000:
            return f"{power_w / 1_000:.3f} кВт"
        else:
            return f"{power_w:.2f} Вт"
    except (ValueError, TypeError):
        return f"{power_w} Вт"

def format_weight(weight_kg):
    """Форматирует вес с автоматическим выбором единиц измерения"""
    try:
        weight_kg = float(weight_kg)
        if weight_kg >= 1000:
            return f"{weight_kg / 1000:.3f} т"
        else:
            return f"{weight_kg:.3f} кг"
    except (ValueError, TypeError):
        return f"{weight_kg} кг"