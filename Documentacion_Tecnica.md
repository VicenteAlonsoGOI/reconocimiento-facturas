# 🛠️ Documentación Técnica: Sistema de Facturación

Este documento detalla la lógica interna del script de automatización para facilitar su mantenimiento futuro.

## 🏗️ Arquitectura del Proyecto
```text
/
├── main.py                 # Orquestador del flujo
├── INICIAR_PROCESO.bat     # Lanzador para usuario final
├── src/
│   ├── extractor.py        # Lógica de PDF/ZIP (pdfplumber + regex)
│   ├── excel_manager.py    # Generación de informes (openpyxl)
│   └── utils.py            # Funciones de limpieza de datos
├── Expedientes/            # Carpeta de entrada (Input)
└── Resultados_Procesados/  # Carpeta de salida (Output)
```

## 🧹 Lógica de Limpieza (Robustez)

### 1. Limpieza de Moneda (`utils.py`)
- Utiliza expresiones regulares para eliminar el símbolo `€` y espacios.
- Convierte el formato español (`.` miles, `,` decimales) al formato estándar de Python (`float`).
- Si el dato no es procesable, devuelve `0.0` para evitar que el script se detenga.

### 2. Limpieza de Fechas (`utils.py`)
- Reemplaza separadores `.` y `-` por `/`.
- Intenta parsear la fecha usando diversos formatos comunes.
- Devuelve siempre el formato `DD/MM/YYYY`.

### 3. Nombres de Archivos
- Se utiliza `re.sub` para eliminar caracteres como `\ / * : ? " < > |` que Windows prohíbe en nombres de archivo, asegurando que el Excel se guarde siempre sin errores.

## 🔍 Motor de Extracción
Ubicado en `extractor.py`, utiliza **Regex (Expresiones Regulares)** para buscar patrones de texto:
- **Número de Factura**: Busca palabras clave como "Factura nº", "Nº Factura", "Invoice".
- **IVAs Múltiples**: El script busca todas las apariciones de porcentajes de IVA y sus importes asociados, acumulándolos en una cadena de texto para el Excel.

## 📦 Despliegue y GitHub
- El proyecto está estructurado para ser autocontenido.
- El `.bat` gestiona las dependencias automáticamente (`pdfplumber`, `openpyxl`).
- Para subir a **GitHub**, se recomienda ignorar las carpetas de datos temporales creando un `.gitignore`.

## ⚙️ Mantenimiento
Para añadir nuevos campos de extracción, simplemente añade el patrón regex en el diccionario `self.patterns` de la clase `InvoiceExtractor`.
