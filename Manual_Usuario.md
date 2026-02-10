# 📖 Manual de Usuario: Automatización de Facturas

Este sistema permite procesar expedientes con facturas en formato ZIP y generar automáticamente informes en Excel con los datos extraídos.

## 🚀 Cómo usar el programa (Paso a Paso)

1. **Preparar los Expedientes**: 
   - Asegúrate de que tus carpetas de expedientes estén dentro de la carpeta llamada `Expedientes`.
   - Cada expediente puede contener uno o varios archivos `.zip`.
   - Dentro de los `.zip` deben estar las facturas en formato `.pdf`.

2. **Iniciar el Proceso**:
   - Haz doble clic en el archivo llamado **`INICIAR_PROCESO.bat`**.
   - Se abrirá una ventana negra (consola). No te preocupes, el programa está trabajando.
   - Si es la primera vez, el programa instalará automáticamente lo necesario.

3. **Esperar a que Finalice**:
   - Verás mensajes indicando qué expediente se está procesando.
   - Al terminar, verás el mensaje: `¡PROCESO FINALIZADO CON ÉXITO!`.
   - Presiona cualquier tecla para cerrar la ventana.

4. **Recoger los Resultados**:
   - Ve a la carpeta **`Resultados_Procesados`**.
   - Allí encontrarás un archivo Excel por cada expediente procesado.

## 📊 ¿Qué datos se extraen?
El sistema busca automáticamente en cada factura:
- **Número de Factura**
- **Fecha** (normalizada a DD/MM/YYYY)
- **Base Imponible**
- **IVA** (si hay varios tipos, se mostrarán todos desglosados)

## ⚠️ Solución de problemas comunes
- **Error de Python**: Asegúrate de tener Python instalado en el ordenador.
- **Rutas de Red**: El programa es compatible con carpetas compartidas. Si el archivo está en red, el lanzador lo gestionará automáticamente.
- **Factura no leída**: Si una factura tiene un formato muy extraño o es una imagen (escaneada), es posible que los datos no se detecten correctamente. En ese caso, aparecerá como "No encontrado" en el Excel.
