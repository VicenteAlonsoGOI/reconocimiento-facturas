# 📖 Manual de Usuario: Automatización de Facturas

Este sistema permite procesar expedientes con facturas en formato ZIP y generar automáticamente informes en Excel con los datos extraídos.

## 🚀 Cómo usar el programa (Paso a Paso)

1. **Preparar los Expedientes**: 
   - Asegúrate de que tus carpetas de expedientes estén dentro de la carpeta llamada `Expedientes`.
   - Cada expediente puede contener uno o varios archivos `.zip`.
   - Dentro de los `.zip` deben estar las facturas en formato `.pdf`.

2. **Iniciar el Proceso**:
   - Haz doble clic en el archivo llamado **`INICIAR_PROCESO_V2.bat`**.
   - Se abrirá una ventana negra (consola).
   - **Importante**: Si es la primera vez que lo usas en ese ordenador, el programa **descargará e instalará automáticamente** todo lo necesario (Python). Solo tienes que esperar y aceptar si te pide permisos.

3. **Esperar a que Finalice**:
   - Verás mensajes indicando qué expediente se está procesando.
   - Al terminar, verás el mensaje: `PROCESO FINALIZADO`.
   - Presiona cualquier tecla para cerrar la ventana.

4. **Recoger los Resultados**:
   - Ve a la carpeta **`Resultados_Procesados`**.
   - Allí encontrarás un archivo Excel por cada expediente procesado.

## 📊 ¿Qué datos se extraen?
El sistema genera un Excel detallado con las siguientes columnas:

- **Datos Generales**: Número de Factura, Fecha de Emisión y Fecha de Cargo.
- **Desglose de Impuestos**:
  - **BI 5% / IVA 5%**: Base y Cuota para el tipo súper reducido.
  - **BI 10% / IVA 10%**: Base y Cuota para el tipo reducido.
  - **BI 21% / IVA 21%**: Base y Cuota para el tipo general.
- **Totales y Validaciones**:
  - **Base Imponible Total**: Suma de todas las bases (según PDF).
  - **Total Factura**: Importe final a pagar (soporta montos negativos para notas de crédito).
  - **CHECK TOTAL**: Columna de comprobación (suma de bases + cuotas) para detectar descuadres.
  - **Fila de Totales**: Suma final de todos los importes del expediente.

### 🆕 Novedades V2.2
- **Soporte para Notas de Crédito**: El sistema ahora procesa correctamente facturas con montos negativos (abonos o devoluciones).
- **Inferencia Automática de IVA**: Si una factura no tiene el desglose de IVA explícito pero sí tiene Base Imponible y Total, el sistema calcula automáticamente el IVA y determina el tipo más probable (5%, 10% o 21%).

### 🛡️ Filtrado Inteligente
El programa incluye un sistema para mantener tus informes limpios:
- **Ignora automáticamente** archivos que no sean facturas (como contratos o cartas).
- **Evita capturas erróneas** descartando documentos donde no se detecte un importe total válido.

## ⚠️ Solución de problemas comunes
- **Error de Python**: Asegúrate de tener Python instalado en el ordenador.
- **Rutas de Red**: El programa es compatible con carpetas compartidas. Si el archivo está en red, el lanzador lo gestionará automáticamente.
- **Factura no leída**: Si una factura tiene un formato muy extraño o es una imagen (escaneada), es posible que los datos no se detecten correctamente. En ese caso, aparecerá como "No encontrado" en el Excel.
