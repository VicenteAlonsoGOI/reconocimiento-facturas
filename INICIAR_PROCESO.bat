@echo off
setlocal
title Automatización de Facturas - Lanzador Profesional

:: Soporte para rutas de red (UNC)
pushd "%~dp0"

echo ======================================================
echo    MODO 'A PRUEBA DE ERRORES' - SISTEMA DE FACTURAS
echo ======================================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado en este equipo.
    echo Por favor, instale Python 3.x para continuar.
    pause
    exit /b
)

echo [1/3] Verificando e instalando librerias necesarias...
python -m pip install --upgrade pip
python -m pip install pdfplumber openpyxl
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las librerias. Verifique su conexion a internet.
    pause
    exit /b
)

echo.
echo [2/3] Iniciando extraccion de facturas...
echo ------------------------------------------------------
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El proceso se detuvo inesperadamente. 
    echo Revise los mensajes arriba para mas detalle.
    pause
    exit /b
)

echo.
echo [3/3] ¡PROCESO FINALIZADO CON EXITO!
echo ------------------------------------------------------
echo Los resultados estan en la carpeta: Resultados_Procesados
echo.
echo Presione cualquier tecla para cerrar...

popd
pause >nul
