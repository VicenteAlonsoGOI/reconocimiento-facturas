from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelManager:
    def __init__(self):
        # Colores corporativos (ejemplo: Azul Oscuro y Gris Claro)
        self.header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        self.header_font = Font(color="FFFFFF", bold=True, size=12)
        
        self.zebra_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        
        self.thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )

    def crear_excel_expediente(self, datos_facturas, output_path):
        """
        Crea un Excel con los datos de múltiples facturas.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Facturas Extraídas"
        
        headers = ["Factura", "Fecha Factura", "Fecha Cargo", "Base Imponible", "Total", "IVA (Desglose)", "Archivo Original"]
        ws.append(headers)
        
        # Estilo para cabecera
        for col, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.fill = self.header_fill
            cell.font = self.header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = self.thin_border
            
        # Añadir datos
        for idx, factura in enumerate(datos_facturas, 2):
            row_data = [
                factura.get('Factura'),
                factura.get('Fecha Factura'),
                factura.get('Fecha Cargo'),
                factura.get('Base Imponible'),
                factura.get('Total'),
                factura.get('IVA'),
                factura.get('Archivo')
            ]
            ws.append(row_data)
            
            # Estilo para filas de datos
            fill = self.zebra_fill if idx % 2 == 0 else None
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=idx, column=col)
                cell.border = self.thin_border
                if fill:
                    cell.fill = fill
                
                # Alinear importes a la derecha
                if headers[col-1] in ["Base Imponible", "Total"]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = Alignment(horizontal="right")
        
        # Ajustar ancho de columnas
        for i, col in enumerate(ws.columns, 1):
            max_length = 0
            column = get_column_letter(i)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 5

        # Añadir filtros
        ws.auto_filter.ref = ws.dimensions
        
        wb.save(output_path)
