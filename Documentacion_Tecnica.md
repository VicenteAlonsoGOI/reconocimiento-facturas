# 🛠️ Documentación Técnica: Sistema de Facturación

Este documento detalla la lógica interna del script de automatización para facilitar su mantenimiento futuro.

## 🏗️ Arquitectura del Proyecto
```text
/
├── main.py                 # Orquestador del flujo
├── INICIAR_PROCESO_V2.bat  # Lanzador inteligente (instala Python si falta)
├── src/
│   ├── extractor.py        # Lógica de PDF/ZIP (Devuelve IVA estructurado)
│   ├── excel_manager.py    # Generación de informes con fórmulas y desglose
│   └── utils.py            # Funciones de limpieza de datos
├── Expedientes/            # Carpeta de entrada (acepta .zip y .pdf directos)
└── Resultados_Procesados/  # Carpeta de salida (Output)
```

## 🧹 Lógica de Limpieza (Robustez)

### 1. Limpieza de Moneda (`utils.py`)
- Detecta el signo negativo **antes** de limpiar el texto para preservarlo.
- Utiliza expresiones regulares para eliminar el símbolo `€` y espacios.
- Convierte el formato español (`.` miles, `,` decimales) al formato estándar de Python (`float`).
- **Soporta montos negativos**: Útil para procesar notas de crédito o abonos.
- Si el dato no es procesable, devuelve `0.0` para evitar que el script se detenga.

### 2. Limpieza de Fechas (`utils.py`)
- Reemplaza separadores `.` y `-` por `/`.
- Intenta parsear la fecha usando diversos formatos comunes.
- Devuelve siempre el formato `DD/MM/YYYY`.

### 3. Nombres de Archivos
- Se utiliza `re.sub` para eliminar caracteres como `\ / * : ? " < > |` que Windows prohíbe en nombres de archivo, asegurando que el Excel se guarde siempre sin errores.

## 🔍 Motor de Extracción
Ubicado en `extractor.py`, utiliza **Regex (Expresiones Regulares)** para buscar patrones de texto:
- **Número de Factura**: Busca palabras clave como "Factura nº", "Nº Factura", "Invoice". Se ha refinado para ignorar etiquetas como "Tlfno" o "Fax".
- **Fechas**: Se extraen por separado la "Fecha de Factura" (emisión) y la "Fecha de Cargo" (vencimiento/cobro).
- **Importes**: Captura tanto la "Base Imponible" como el "Total" de la factura.
- **IVAs Múltiples (V2)**: El script analiza el texto para extraer **Base Imponible** y **Cuota** por cada tipo de IVA (5%, 10%, 21%), devolviendo una estructura de datos detallada en lugar de texto plano.
- **Soporte para Montos Negativos (V2.2)**: Los patrones regex incluyen `-?` (signo negativo opcional) para capturar correctamente:
  - Facturas rectificativas (notas de crédito)
  - Abonos y devoluciones
  - Ajustes con importes negativos
  - Ejemplo: `-78,26 €` se captura correctamente como -78.26
- **Inferencia de IVA (V2.2)**: Si no se encuentra desglose explícito de IVA pero sí hay Base Imponible y Total:
  1. Calcula el IVA como: `IVA = Total - Base Imponible`
  2. Determina el ratio: `(IVA / Base) * 100`
  3. Asigna al tipo más cercano (21%, 10% o 5%) con tolerancia de ±2%
  4. Si no coincide con ninguno, asume 21% por defecto

## 🛡️ Lógica de Filtrado Inteligente
Para asegurar que los informes contengan solo facturas válidas, se aplican dos niveles de filtrado:
1. **Filtro por Nombre**: Se omiten archivos que contengan palabras como "CONTRATO" o "CARTA" en su nombre.
2. **Filtro por Contenido**: Si tras procesar el PDF no se encuentra un Número de Factura Y el Total es 0, el documento se considera irrelevante y no se añade al Excel.

## 📦 Despliegue y GitHub
- El proyecto está estructurado para ser autocontenido.
- El script **`INICIAR_PROCESO_V2.bat`** es capaz de detectar si Python está instalado. Si no lo está, lo descarga e instala automáticamente sin intervención del usuario.
- Gestiona las dependencias (`pdfplumber`, `openpyxl`) mediante `pip`.
- Los informes generados y los datos de entrada están excluidos en el `.gitignore`.

## ⚙️ Mantenimiento
Para añadir nuevos campos de extracción o ajustar el filtrado:
- Patrones: Añade el patrón regex en el diccionario `self.patterns` en `extractor.py`.
- Reglas de exclusión: Modifica el método `extraer_datos_pdf` en `extractor.py`.
