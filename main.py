import os
import sys
from src.extractor import InvoiceExtractor
from src.excel_manager import ExcelManager
from src.utils import limpiar_nombre_archivo

def procesar_todo(input_folder, output_base):
    extractor = InvoiceExtractor()
    excel_gen = ExcelManager()
    
    if not os.path.exists(input_folder):
        print(f"Error: La carpeta de entrada no existe: {input_folder}")
        return

    if not os.path.exists(output_base):
        os.makedirs(output_base)

    print(f"Iniciando proceso en: {input_folder}")
    
    # Recorrer subcarpetas de expedientes
    for item in os.listdir(input_folder):
        expediente_path = os.path.join(input_folder, item)
        
        if os.path.isdir(expediente_path):
            print(f"--- Procesando Expediente: {item} ---")
            todas_las_facturas = []
            
            # Buscar archivos (ZIPs o PDFs) dentro del expediente
            for file in os.listdir(expediente_path):
                file_path = os.path.join(expediente_path, file)
                
                # Caso 1: Archivo ZIP
                if file.lower().endswith('.zip'):
                    print(f"  Analizando ZIP: {file}...")
                    datos_zip = extractor.procesar_zip(file_path)
                    todas_las_facturas.extend(datos_zip)
                
                # Caso 2: PDF directo
                elif file.lower().endswith('.pdf'):
                    print(f"  Analizando PDF directo: {file}...")
                    datos_pdf = extractor.extraer_datos_pdf(file_path)
                    if datos_pdf:
                        todas_las_facturas.extend([datos_pdf] if isinstance(datos_pdf, dict) else datos_pdf)
            
            # Si hay facturas, generar el Excel para este expediente
            if todas_las_facturas:
                nombre_excel = f"Reporte_Facturas_{limpiar_nombre_archivo(item)}.xlsx"
                output_path = os.path.join(output_base, nombre_excel)
                
                print(f"  Generando Excel: {nombre_excel} ({len(todas_las_facturas)} facturas)")
                excel_gen.crear_excel_expediente(todas_las_facturas, output_path)
            else:
                print(f"  Aviso: No se encontraron facturas en el expediente {item}")

    print("\nProceso finalizado con éxito.")

if __name__ == "__main__":
    # Configuración de rutas
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PATH_EXPEDIENTES = os.path.join(BASE_DIR, "Expedientes")
    PATH_RESULTADOS = os.path.join(BASE_DIR, "Resultados_Procesados")
    
    procesar_todo(PATH_EXPEDIENTES, PATH_RESULTADOS)
