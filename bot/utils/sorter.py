import re
def natural_sort_key(text):
    # Разбивает строку на числовые и текстовые части
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', text)]