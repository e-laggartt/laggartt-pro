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
    # utils/calculator.py (дополнения)


def parse_competitor_name(name):
    """
    Парсинг наименований конкурентов для автоматического определения параметров
    """
    name_str = str(name).upper()
    
    patterns = [
        # VC 22-500-600, VK 30-600-1200
        r'(V[KC])\s*(\d+)[-\s](\d+)[-\s](\d+)',
        # ЛК 11-504, ЛК 11-504-900
        r'[ЛL][КK]\s*(\d+)[-\s](\d+)(?:[-\s](\d+))?',
        # тип 10-400-1000
        r'ТИП\s*(\d+)[-\s](\d+)[-\s](\d+)',
        # 10-400-1000
        r'(\d+)[-\s](\d+)[-\s](\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name_str)
        if match:
            return extract_parameters_from_match(match, pattern)
    
    return None

def extract_parameters_from_match(match, pattern):
    """
    Извлечение параметров из regex match
    """
    groups = match.groups()
    
    if 'V' in pattern:
        # VK/VC формат: VK 30-600-1200
        connection_map = {
            'VK': 'VK-правое',
            'VC': 'VK-левое'
        }
        return {
            'type': groups[1] if len(groups) >= 2 else None,
            'height': int(groups[2]) if len(groups) >= 3 and groups[2] else None,
            'length': int(groups[3]) if len(groups) >= 4 and groups[3] else None,
            'connection': connection_map.get(groups[0], 'VK-правое')
        }
    else:
        # Другие форматы
        return {
            'type': groups[0] if groups[0] else None,
            'height': int(groups[1]) if len(groups) >= 2 and groups[1] else None,
            'length': int(groups[2]) if len(groups) >= 3 and groups[2] else None,
            'connection': 'K-боковое'
        }

def find_meteor_equivalent(parameters, sheets_data):
    """
    Поиск эквивалента METEOR по параметрам
    """
    if not parameters:
        return None
    
    for sheet_name, df in sheets_data.items():
        # Проверка соответствия подключения
        sheet_connection = sheet_name.split()[0]  # "VK-правое" -> "VK-правое"
        if parameters.get('connection') == sheet_connection:
            # Поиск по размерам в наименованиях
            height = parameters.get('height')
            length = parameters.get('length')
            
            if height and length:
                pattern = f"/{height}мм/{length}мм"
                matches = df[df['Наименование'].str.contains(pattern, na=False)]
                
                if not matches.empty:
                    product = matches.iloc[0]
                    return {
                        'art': product['Артикул'],
                        'name': product['Наименование'],
                        'sheet': sheet_name
                    }
    
    return None