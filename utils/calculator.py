# utils/calculator.py
import re

def parse_quantity(value):
    """
    Парсинг количеств с поддержкой формул
    """
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

def calculate_brackets(radiator_type, length, height, bracket_type, qty=1):
    """
    Универсальная функция расчета кронштейнов
    """
    brackets = []
    
    if bracket_type == "Без кронштейнов":
        return brackets
    
    if bracket_type == "Настенные кронштейны":
        brackets = calculate_wall_brackets(radiator_type, length, height, qty)
    elif bracket_type == "Напольные кронштейны":
        brackets = calculate_floor_brackets(radiator_type, length, height, qty)
    
    return brackets

def calculate_wall_brackets(radiator_type, length, height, qty=1):
    """
    Расчет настенных кронштейнов
    """
    brackets = []
    
    if radiator_type in ["10", "11"]:
        brackets = [("К9.2L", 2 * qty), ("К9.2R", 2 * qty)]
        if 1700 <= length <= 2000:
            brackets.append(("К9.3-40", 1 * qty))
            
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
                qty_br = 2 * qty
            elif 1700 <= length <= 2000:
                qty_br = 3 * qty
            else:
                qty_br = 0
                
            if qty_br:
                brackets.append((art, qty_br))
    
    return brackets

def calculate_floor_brackets(radiator_type, length, height, qty=1):
    """
    Расчет напольных кронштейнов
    """
    brackets = []
    
    if radiator_type in ["10", "11"]:
        art_map = {
            300: "КНС450", 
            400: "КНС450",
            500: "КНС450", 
            600: "КНС450",
            900: "КНС450"
        }
        
        if height in art_map:
            main_art = art_map[height]
            brackets.append((main_art, 2 * qty))
            
            if 1700 <= length <= 2000:
                brackets.append(("КНС430", 1 * qty))
                
    elif radiator_type in ["20", "21", "22", "30", "33"]:
        art_map = {
            300: "КНС450", 
            400: "КНС450",
            500: "КНС450",
            600: "КНС450", 
            900: "КНС450"
        }
        
        if height in art_map:
            main_art = art_map[height]
            if 400 <= length <= 1600:
                brackets.append((main_art, 2 * qty))
            elif 1700 <= length <= 2000:
                brackets.append((main_art, 3 * qty))
    
    return brackets

def parse_competitor_name(name):
    """
    Парсинг наименований конкурентов для автоматического определения параметров
    """
    patterns = [
        r'тип\s*([ckv])\s*(\d+)[-\s](\d+)[-\s](\d+)',
        r'[лl][кk]\s*(\d+)[-\s](\d+)',
        r'([ckv])\s*(\d+)[-\s](\d+)[-\s](\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(name), re.IGNORECASE)
        if match:
            return extract_parameters(match)
    
    return None

def extract_parameters(match):
    """
    Извлечение параметров из regex match
    """
    # Заглушка - нужно доработать под конкретные форматы
    return {
        'type': match.group(1) if match.groups() >= 1 else None,
        'height': int(match.group(2)) if match.groups() >= 2 else None,
        'length': int(match.group(3)) if match.groups() >= 3 else None
    }