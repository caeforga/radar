@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM Script de compilación rápida para Windows
REM Ejecutar: build.bat

echo ================================================================================
echo        COMPILACION DE EJECUTABLE - SOFTWARE RADAR
echo ================================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en el PATH
    echo Instala Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar si estamos en entorno virtual
if defined VIRTUAL_ENV (
    echo [INFO] Entorno virtual activo: %VIRTUAL_ENV%
) else (
    echo [INFO] Ejecutando en entorno global
)
echo.

REM Preguntar si quiere instalar PyInstaller
echo Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PyInstaller no esta instalado
    echo.
    set "install="
    set /p "install=Deseas instalarlo ahora? (S/N): "
    
    if /i "!install!"=="S" goto install_pyinstaller
    if /i "!install!"=="s" goto install_pyinstaller
    if /i "!install!"=="SI" goto install_pyinstaller
    if /i "!install!"=="si" goto install_pyinstaller
    if /i "!install!"=="Y" goto install_pyinstaller
    if /i "!install!"=="y" goto install_pyinstaller
    if /i "!install!"=="YES" goto install_pyinstaller
    
    echo.
    echo Cancelado por el usuario
    pause
    exit /b 1
    
    :install_pyinstaller
    echo.
    echo Instalando PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
    echo [OK] PyInstaller instalado correctamente
    echo.
)

echo [OK] PyInstaller disponible
echo.

REM Ejecutar script de construcción
echo ================================================================================
echo Iniciando construccion del ejecutable...
echo ================================================================================
echo.

python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo [EXITO] Compilacion completada!
    echo ================================================================================
    echo.
    echo El ejecutable esta en: dist\SoftwareRadar.exe
    echo.
    set "test="
    set /p "test=Deseas ejecutar el archivo ahora? (S/N): "
    
    if /i "!test!"=="S" goto run_exe
    if /i "!test!"=="s" goto run_exe
    if /i "!test!"=="SI" goto run_exe
    if /i "!test!"=="si" goto run_exe
    if /i "!test!"=="Y" goto run_exe
    if /i "!test!"=="y" goto run_exe
    
    goto end_script
    
    :run_exe
    echo.
    echo Ejecutando SoftwareRadar.exe...
    start dist\SoftwareRadar.exe
    goto end_script
) else (
    echo.
    echo ================================================================================
    echo [ERROR] Hubo un problema durante la compilacion
    echo ================================================================================
    echo.
    echo Revisa los mensajes de error anteriores
    echo Consulta BUILD_EXECUTABLE.md para mas ayuda
)

:end_script

echo.
pause

