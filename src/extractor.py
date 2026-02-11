import os
import zipfile
import tempfile
import pdfplumber
import re
from .utils import limpiar_moneda, limpiar_fecha

class InvoiceExtractor:
    def __init__(self):
        # Patrones regex para búsqueda de datos
        self.patterns = {
            'numero_factura': [
                # Buscar específicamente códigos que parezcan facturas (evitando palabras comunes como Tlfno)
                r'(?:N.|Nº|N|No|No.|Número|Factura|Invoice)\s*(?:de\s+)?factura\s*[:\s]*(?!(?:Tlfno|Tel|Teléfono|Fax))([a-zA-Z0-9\-/.\\]{3,})',
                r'Nº\s*(?!(?:Tlfno|Tel|Teléfono|Fax))([a-zA-Z0-9\-/.\\]{5,})',
                r'Factura\s+(?!(?:Tlfno|Tel|Teléfono|Fax))([a-zA-Z0-9\-/.\\]{5,})',
            ],
            'fecha_factura': [
                r'Fecha\s*(?:de\s+)?(?:factura|emisión|expedición)\s*[:\s]*(\d{2}[-./]\d{2}[-./]\d{2,4})',
                r'Fecha\s*[:\s]*(\d{2}[-./]\d{2}[-./]\d{2,4})',
            ],
            'fecha_cargo': [
                r'Fecha\s*(?:de\s+)?cargo\s*[:\s]*(\d{2}[-./]\d{2}[-./]\d{2,4})',
            ],
            'base_imponible': [
                r'Base\s*imponible\s*[:\s]*([\d.,]+)',
                r'TOTAL\s*BASE\s*[:\s]*([\d.,]+)',
            ],
            'total': [
                r'TOTAL\s*(?:IMPORTE\s*)?FACTURA\s*[:\s]*([\d.,]+)',
                r'TOTAL\s*A\s*PAGAR\s*[:\s]*([\d.,]+)',
                r'IMPORTE\s*TOTAL\s*[:\s]*([\d.,]+)',
                # Buscar un total genérico si los anteriores fallan (con precaución)
                r'TOTAL\s*[:\s]*([\d.,]+)\s*€',
            ],
            'iva': [
                # Formato: 21,00 % s/68,14 14,31 (captura 21% y 14,31)
                r'(\d{1,2})\s*,\s*00\s*%\s*s/[\d.,]+\s+([\d.,]+)',
                # Formato: IVA (21%) ... 14,31
                r'\((\d{1,2})%\)[^\n]+?\s+([\d.,]+)(?:\s|$)',
                r'IVA\s*(\d{1,2})%\s*[:\s]*([\d.,]+)',
            ]
        }

    def extraer_datos_pdf(self, pdf_path):
        """Extrae texto de un PDF y busca los campos requeridos."""
        filename = os.path.basename(pdf_path).lower()
        
        # Filtro inicial por nombre de archivo
        if any(x in filename for x in ['contrato', 'carta', 'firma']):
            return None

        datos = {
            'Factura': 'No encontrado',
            'Fecha Factura': 'No encontrado',
            'Fecha Cargo': 'No encontrado',
            'Base Imponible': 0.0,
            'Total': 0.0,
            'IVA': [], # Lista de tuplas (porcentaje, importe)
            'Archivo': os.path.basename(pdf_path)
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto_completo = ""
                for page in pdf.pages:
                    texto_completo += page.extract_text() + "\n"
                
                # Buscar Número de Factura
                for p in self.patterns['numero_factura']:
                    match = re.search(p, texto_completo, re.IGNORECASE)
                    if match:
                        f_candidate = match.group(1).strip()
                        # Validar que no sea una palabra común prohibida si se capturó algo por error
                        if not re.match(r'^(serie|import|total|fecha|factura)$', f_candidate, re.IGNORECASE):
                            datos['Factura'] = f_candidate
                            break
                
                # Buscar Fecha Factura
                for p in self.patterns['fecha_factura']:
                    match = re.search(p, texto_completo, re.IGNORECASE)
                    if match:
                        datos['Fecha Factura'] = limpiar_fecha(match.group(1))
                        break

                # Buscar Fecha Cargo
                for p in self.patterns['fecha_cargo']:
                    match = re.search(p, texto_completo, re.IGNORECASE)
                    if match:
                        datos['Fecha Cargo'] = limpiar_fecha(match.group(1))
                        break
                
                # Buscar Base Imponible
                for p in self.patterns['base_imponible']:
                    match = re.search(p, texto_completo, re.IGNORECASE)
                    if match:
                        datos['Base Imponible'] = limpiar_moneda(match.group(1))
                        break
                
                # Buscar Total
                for p in self.patterns['total']:
                    match = re.search(p, texto_completo, re.IGNORECASE)
                    if match:
                        datos['Total'] = limpiar_moneda(match.group(1))
                        break
                
                # Buscar IVAs (pueden ser múltiples) y estructurarlos
                ivas_estructurados = {
                    '5': {'base': 0.0, 'cuota': 0.0},
                    '10': {'base': 0.0, 'cuota': 0.0},
                    '21': {'base': 0.0, 'cuota': 0.0}
                }
                
                # Patrones mejorados para capturar (Base, Tipo, Cuota) cuando sea posible
                # Caso 1: Estándar (Base ... Tipo ... Cuota) o (Tipo ... Base ... Cuota)
                # Ejemplo: 21% s/100.00 21.00
                patrones_detallados = [
                    r'(\d{1,2})\s*%\s*s/\s*([\d.,]+)\s+([\d.,]+)',  # 21% s/ 100.00 21.00
                    r'Base\s*[:\s]*([\d.,]+)\s+IVA\s*[:\s]*(\d{1,2})\s*%\s+Cuota\s*[:\s]*([\d.,]+)', # Base: 100 IVA: 21% Cuota: 21
                    r'(?:Base|BI)\s*(\d{1,2})%\s*[:\s]*([\d.,]+)', # Base 21%: 100.00 (Solo Base)
                    r'IVA\s*(\d{1,2})%\s*[:\s]*([\d.,]+)', # IVA 21%: 21.00 (Solo Cuota)
                    r'\((\d{1,2})%\)[^\n]+?\s+([\d.,]+)(?:\s|$)' # (21%) ... 21.00
                ]

                # Primera pasada: Buscar bloques completos (Base + Cuota)
                for p in patrones_detallados[:2]:
                    matches = re.finditer(p, texto_completo, re.IGNORECASE)
                    for match in matches:
                        try:
                            # Detectar orden de grupos según patrón
                            if 's/' in p: # Patrón 1: Tipo, Base, Cuota
                                tipo = match.group(1)
                                base = float(limpiar_moneda(match.group(2)))
                                cuota = float(limpiar_moneda(match.group(3)))
                            else: # Patrón 2: Base, Tipo, Cuota
                                base = float(limpiar_moneda(match.group(1)))
                                tipo = match.group(2)
                                cuota = float(limpiar_moneda(match.group(3)))
                            
                            if tipo in ivas_estructurados:
                                ivas_estructurados[tipo]['base'] += base
                                ivas_estructurados[tipo]['cuota'] += cuota
                        except:
                            continue

                # Segunda pasada: Buscar datos sueltos si no se encontraron completos
                # Si una factura tiene desglose simple, intentamos capturar al menos la cuota o la base
                for p in patrones_detallados[2:]:
                    matches = re.finditer(p, texto_completo, re.IGNORECASE)
                    for match in matches:
                        try:
                            tipo = match.group(1)
                            valor = float(limpiar_moneda(match.group(2)))
                            
                            if tipo in ivas_estructurados:
                                # Diferenciar si capturamos Base o Cuota según el patrón
                                if 'Base' in p or 'BI' in p:
                                    # Si ya tenemos base (de la pasada anterior), sumamos; si no, asignamos
                                    # Evitar duplicar si ya se capturó en la pasada detallada
                                    if ivas_estructurados[tipo]['base'] == 0.0: 
                                        ivas_estructurados[tipo]['base'] += valor
                                else: # Asumimos Cuota
                                    if ivas_estructurados[tipo]['cuota'] == 0.0:
                                        ivas_estructurados[tipo]['cuota'] += valor
                        except:
                            continue
                
                # Post-procesado: Si tenemos Cuota pero Base es 0, intentar calcular Base (Cuota / (Tipo/100))
                # Esto es útil si el OCR falló en leer la base pero leyó bien la cuota
                for tipo, datos_iva in ivas_estructurados.items():
                    if datos_iva['cuota'] > 0 and datos_iva['base'] == 0:
                        try:
                            tasa = float(tipo)
                            datos_iva['base'] = round(datos_iva['cuota'] / (tasa / 100), 2)
                        except:
                            pass
                    # Y viceversa: Si tenemos Base pero Cuota 0
                    elif datos_iva['base'] > 0 and datos_iva['cuota'] == 0:
                        try:
                            tasa = float(tipo)
                            datos_iva['cuota'] = round(datos_iva['base'] * (tasa / 100), 2)
                        except:
                            pass

                # Inferencia de IVA: Si no hay ningún desglose pero sí Base Imponible y Total
                # Esto maneja facturas sin desglose explícito de IVA
                if all(datos_iva['cuota'] == 0 for datos_iva in ivas_estructurados.values()):
                    if datos['Base Imponible'] > 0 and datos['Total'] > 0:
                        iva_total = datos['Total'] - datos['Base Imponible']
                        
                        if abs(iva_total) > 0.01:  # Tolerancia para evitar errores de redondeo
                            # Inferir tipo de IVA según ratio
                            ratio = abs((iva_total / datos['Base Imponible']) * 100)
                            
                            # Asignar al tipo más cercano con tolerancia ±2%
                            if abs(ratio - 21) < 2:
                                tipo_inferido = '21'
                            elif abs(ratio - 10) < 2:
                                tipo_inferido = '10'
                            elif abs(ratio - 5) < 2:
                                tipo_inferido = '5'
                            else:
                                tipo_inferido = '21'  # Por defecto 21% si no coincide
                            
                            ivas_estructurados[tipo_inferido]['base'] = datos['Base Imponible']
                            ivas_estructurados[tipo_inferido]['cuota'] = round(iva_total, 2)

                datos['IVA'] = ivas_estructurados
                
                # Filtro final: Si no hay factura ni total (en valor absoluto), descartar.
                # Permitimos montos negativos (notas de crédito)
                if datos['Factura'] == 'No encontrado' and abs(datos['Total']) == 0.0:
                    return None
                
                # Filtro extra de seguridad: Si el total es 0 (no negativo), y la factura parece sospechosa, descartar
                # Permitimos negativos porque son notas de crédito válidas
                if datos['Total'] == 0.0 and (len(datos['Factura']) < 3 or datos['Factura'].isalpha()):
                    return None

        except Exception as e:
            print(f"Error procesando {pdf_path}: {e}")
            return None
            
        return datos

    def procesar_zip(self, zip_path):
        """Extrae facturas de un ZIP y devuelve lista de datos."""
        lista_datos = []
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                    
                    for root, _, files in os.walk(tmpdir):
                        for file in files:
                            if file.lower().endswith('.pdf'):
                                pdf_path = os.path.join(root, file)
                                datos = self.extraer_datos_pdf(pdf_path)
                                if datos: # Solo añadir si pasó los filtros
                                    lista_datos.append(datos)
            except Exception as e:
                print(f"Error con el ZIP {zip_path}: {e}")
        
        return lista_datos
