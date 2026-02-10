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
                # Buscar específicamente códigos que parezcan facturas (letras y números mixtos, guiones, etc)
                r'(?:N.|Nº|N|No|No.|Número|Factura|Invoice)\s*(?:de\s+)?factura\s*[:\s]*([a-zA-Z0-9\-/.\\]{3,})',
                r'Nº\s*([a-zA-Z0-9\-/.\\]{5,})',
                r'Factura\s+([a-zA-Z0-9\-/.\\]{5,})',
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
                        datos['Factura'] = match.group(1).strip()
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
                
                # Buscar IVAs (pueden ser múltiples)
                ivas_encontrados = []
                for p in self.patterns['iva']:
                    matches = re.finditer(p, texto_completo, re.IGNORECASE)
                    for match in matches:
                        if len(match.groups()) == 2:
                            porc = match.group(1)
                            imp = limpiar_moneda(match.group(2))
                            ivas_encontrados.append(f"{porc}%: {imp}")
                        else:
                            imp = limpiar_moneda(match.group(1))
                            ivas_encontrados.append(f"IVA: {imp}")
                
                datos['IVA'] = ", ".join(list(set(ivas_encontrados))) if ivas_encontrados else "0%"
                
        except Exception as e:
            print(f"Error procesando {pdf_path}: {e}")
            
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
                                lista_datos.append(datos)
            except Exception as e:
                print(f"Error con el ZIP {zip_path}: {e}")
        
        return lista_datos
