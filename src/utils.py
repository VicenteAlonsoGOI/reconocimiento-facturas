import re
from datetime import datetime

def limpiar_moneda(texto):
    """
    Convierte un string tipo '1.234,56 €' o '56,00' a float.
    Maneja puntos de miles y comas decimales (formato español).
    Soporta montos negativos (notas de crédito/abono).
    """
    if not texto:
        return 0.0
    
    # Detectar si es negativo ANTES de limpiar
    es_negativo = '-' in texto
    
    # Eliminar símbolo de euro y espacios
    limpio = texto.replace('€', '').strip()
    
    try:
        # Si tiene punto de miles y coma decimal (ej: 1.234,56)
        if '.' in limpio and ',' in limpio:
            limpio = limpio.replace('.', '').replace(',', '.')
        # Si solo tiene coma decimal (ej: 56,00)
        elif ',' in limpio:
            limpio = limpio.replace(',', '.')
        
        # Eliminar cualquier otro carácter no numérico excepto el punto decimal y signo negativo
        limpio = re.sub(r'[^\d.-]', '', limpio)
        
        valor = float(limpio)
        
        # Aplicar signo negativo si se detectó y el valor es positivo
        if es_negativo and valor > 0:
            valor = -valor
            
        return valor
    except (ValueError, TypeError):
        return 0.0

def limpiar_fecha(texto):
    """
    Detecta formatos variados (DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY)
    y los normaliza a DD/MM/YYYY.
    """
    if not texto:
        return ""
    
    # Normalizar separadores a '/'
    normalizada = texto.replace('.', '/').replace('-', '/').strip()
    
    # Intentar parsear para validar
    formatos = ['%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d']
    for fmt in formatos:
        try:
            dt = datetime.strptime(normalizada, fmt)
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            continue
            
    return normalizada # Si no coincide, devolvemos la normalizada por si acaso

def limpiar_nombre_archivo(nombre):
    """
    Sustituye caracteres prohibidos en nombres de archivo por guiones.
    """
    return re.sub(r'[\\/*?:"<>|]', '-', nombre)

if __name__ == "__main__":
    # Tests rápidos
    print(f"Moneda: {limpiar_moneda('1.234,56 €')} == 1234.56")
    print(f"Fecha: {limpiar_fecha('10.02.2026')} == 10/02/2026")
    print(f"Archivo: {limpiar_nombre_archivo('factura/2024*final.pdf')} == factura-2024-final.pdf")
