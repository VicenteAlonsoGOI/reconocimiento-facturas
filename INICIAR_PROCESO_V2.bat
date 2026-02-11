@echo off
:: Script de inicio robusto para Reconocimiento de Facturas V2
:: Autor: Equipo IA
:: Fecha: 2026-02-11

setlocal
title Instalador y Lanzador de Facturas V2

:: Detectar si estamos en una ruta UNC (\\servidor\carpeta)
set "SCRIPT_DIR=%~dp0"
echo %SCRIPT_DIR% | findstr /B "\\\\" >nul
if %errorlevel% equ 0 (
    echo [!] Detectada ruta UNC. Mapeando temporalmente...
    :: Mapear a unidad Z: temporalmente
    pushd "%SCRIPT_DIR%"
    if %errorlevel% neq 0 (
        echo [X] Error: No se pudo acceder a la ruta de red.
        echo     Asegurate de tener permisos en: %SCRIPT_DIR%
        pause
        exit /b 1
    )
    echo [V] Ruta mapeada correctamente.
)

echo ==================================================
echo      INICIANDO SISTEMA DE FACTURAS V2
echo ==================================================
echo.

:: 1. Verificar si Python esta en el sistema
echo [*] Verificando instalacion de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python no detectado. Se procedera a la instalacion.
    goto :INSTALL_PYTHON
) else (
    echo [V] Python detectado.
    goto :CHECK_DEPS
)

:INSTALL_PYTHON
echo.
echo [!] ATENCION: Este proceso descargara e instalara Python automaticamente.
echo     Por favor, espere y acepte los permisos si se solicitan.
echo.
timeout /t 3

:: Descargar Python 3.12 (Instalador Web) usando PowerShell
echo [*] Descargando instalador...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe' -OutFile 'python_installer.exe'"

if not exist python_installer.exe (
    echo [X] Error: No se pudo descargar el instalador. Verifique su internet.
    pause
    exit /b
)

:: Instalar
echo [*] Instalando Python (esto puede tardar unos minutos)...
:: InstallAllUsers=0 instala en %LocalAppData% (no requiere admin normalmente)
start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

:: Limpiar
del python_installer.exe

:: Intentar añadir al PATH de la sesión actual (Asumiendo ruta por defecto)
set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312\Scripts\;%LocalAppData%\Programs\Python\Python312\"

:: Verificar instalacion
echo [*] Verificando nueva instalacion...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Aviso: Python se ha instalado pero es necesario reiniciar la ventana.
    echo     Por favor, cierra esta ventana y vuelve a ejecutar el archivo.
    pause
    exit /b
)
echo [V] Python instalado correctamente.

:CHECK_DEPS
echo.
echo [*] Verificando librerias necesarias...
:: Instalar dependencias
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [!] Error instalando librerias.
    pause
    exit /b
)
echo [V] Librerias listas.

:RUN_APP
echo.
echo ==================================================
echo      EJECUTANDO PROCESAMIENTO
echo ==================================================
echo.
python main.py

echo.
echo ==================================================
echo      PROCESO FINALIZADO
echo ==================================================
echo.

:: Deshacer mapeo UNC si se usó
popd 2>nul

pause
