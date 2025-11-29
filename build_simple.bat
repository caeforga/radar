@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
REM Script simple de compilacion - Metodo directo

echo ================================================================================
echo   COMPILACION SIMPLE - SOFTWARE RADAR
echo ================================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Instalar PyInstaller si no esta
echo Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
    echo.
)

echo [OK] PyInstaller listo
echo.

REM Limpiar builds anteriores
echo Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo.

echo ================================================================================
echo Compilando... (Esto tomara 5-10 minutos)
echo ================================================================================
echo.

REM Compilar (metodo simple)
python -m PyInstaller ^
  --name=SoftwareRadar ^
  --onefile ^
  --windowed ^
  --add-data=imagenes;imagenes ^
  --collect-all=customtkinter ^
  --collect-all=matplotlib ^
  --hidden-import=roboticstoolbox ^
  --hidden-import=numpy ^
  --hidden-import=PIL ^
  --hidden-import=serial ^
  --hidden-import=ComSerial ^
  --hidden-import=GPS ^
  --hidden-import=CargaSensor ^
  --hidden-import=Interpretacion ^
  --noconfirm ^
  run.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo [EXITO] Ejecutable creado en: dist\SoftwareRadar.exe
    echo ================================================================================
    echo.
    
    REM Mostrar tamaño
    for %%A in (dist\SoftwareRadar.exe) do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo Tamaño: !sizeMB! MB
    )
    
    echo.
    set "test="
    set /p "test=Ejecutar ahora? (S/N): "
    
    if /i "!test!"=="S" start dist\SoftwareRadar.exe
    if /i "!test!"=="s" start dist\SoftwareRadar.exe
) else (
    echo.
    echo [ERROR] Hubo un problema
    echo Revisa los mensajes anteriores
)

echo.
pause

