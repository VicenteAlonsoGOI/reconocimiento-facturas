# Sistema de Reconocimiento de Facturas V2.2

Sistema automatizado para extraer datos de facturas en PDF y generar reportes en Excel.

## 🚀 Inicio Rápido

1. **Descarga el proyecto** en tu ordenador
2. **Coloca tus facturas** (archivos PDF o ZIP) en la carpeta `Expedientes/`
3. **Ejecuta** `INICIAR_PROCESO_V2.bat`
4. **Encuentra los resultados** en la carpeta `Resultados_Procesados/`

## 📋 Requisitos

- **Windows** 7 o superior
- **Conexión a Internet** (solo para la primera ejecución, para instalar Python automáticamente)

**NOTA**: No necesitas instalar nada manualmente. El script `INICIAR_PROCESO_V2.bat` instalará Python y todas las dependencias automáticamente la primera vez que lo ejecutes.

## 📁 Estructura del Proyecto

```
Reconocimiento de Facturas/
├── INICIAR_PROCESO_V2.bat    # Script principal (ejecutar este archivo)
├── main.py                    # Código principal
├── requirements.txt           # Dependencias Python
├── src/                       # Código fuente
│   ├── extractor.py          # Extracción de datos PDF
│   ├── excel_manager.py      # Generación de Excel
│   └── utils.py              # Utilidades
├── Expedientes/              # COLOCA AQUÍ TUS PDFs/ZIPs
├── Resultados_Procesados/    # Aquí se guardan los Excel generados
├── Manual_Usuario.md         # Manual de usuario
└── Documentacion_Tecnica.md  # Documentación técnica
```

## 📖 Documentación

- **[Manual de Usuario](Manual_Usuario.md)**: Guía completa de uso
- **[Documentación Técnica](Documentacion_Tecnica.md)**: Detalles de implementación

## ✨ Características

- ✅ Extracción automática de datos de facturas
- ✅ Soporte para múltiples tipos de IVA (5%, 10%, 21%)
- ✅ Soporte completo para montos negativos (notas de crédito)
- ✅ Inferencia automática de IVA cuando no está desglosado
- ✅ Validación automática con columna CHECK TOTAL
- ✅ Procesamiento de archivos ZIP
- ✅ Instalación automática de dependencias

## 🆕 Novedades V2.2

- **Soporte Completo para Montos Negativos**: Procesa correctamente facturas con importes negativos (notas de crédito, abonos, devoluciones)
- **Inferencia Automática de IVA**: Calcula el IVA automáticamente cuando no está desglosado explícitamente
- **Mejoras en Extracción**: Patrones regex mejorados para mayor precisión

## 🛠️ Solución de Problemas

Si encuentras algún problema:

1. **Verifica** que tienes conexión a Internet (solo primera vez)
2. **Asegúrate** de que los PDFs están en la carpeta `Expedientes/`
3. **Consulta** el [Manual de Usuario](Manual_Usuario.md) para más detalles

## 📝 Licencia

Uso interno - Gesico

## 👥 Autor

Equipo IA Vicente - Gesico
