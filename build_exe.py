"""
Script de construcción del ejecutable para Software Radar.

Este script configura y ejecuta PyInstaller para crear un ejecutable independiente.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

print("=" * 70)
print("🚀 CONSTRUCCIÓN DE EJECUTABLE - SOFTWARE RADAR")
print("=" * 70)
print()

# Verificar que estamos en el directorio correcto
if not os.path.exists("mejorada.py"):
    print("❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto")
    sys.exit(1)

# Limpiar builds anteriores
print("🧹 Limpiando builds anteriores...")
dirs_to_clean = ["build", "dist", "__pycache__"]
for dir_name in dirs_to_clean:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
        print(f"   ✓ Eliminado: {dir_name}")

# Buscar archivos .spec antiguos
for spec_file in Path(".").glob("*.spec"):
    spec_file.unlink()
    print(f"   ✓ Eliminado: {spec_file}")

print()
print("📦 Verificando PyInstaller...")

# Verificar si PyInstaller está instalado
try:
    import PyInstaller
    print(f"   ✓ PyInstaller {PyInstaller.__version__} instalado")
except ImportError:
    print("   ⚠ PyInstaller no está instalado")
    print("   📥 Instalando PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("   ✓ PyInstaller instalado correctamente")

print()
print("🔨 Construyendo ejecutable...")
print("   (Esto puede tomar varios minutos...)")
print()

# Comando base de PyInstaller (usar módulo Python)
cmd = [
    sys.executable,  # Python actual
    "-m", "PyInstaller",  # Ejecutar PyInstaller como módulo
    "--name=SoftwareRadar",
    "--onefile",
    "--windowed",
]

# Agregar icono si existe
icon_path = "assets/images/Icono radar.png"
if not os.path.exists(icon_path):
    icon_path = "imagenes/Icono radar.png"
if os.path.exists(icon_path):
    cmd.append(f"--icon={icon_path}")
    print(f"   ✓ Icono: {icon_path}")
else:
    print("   ⚠ Icono no encontrado, usando icono por defecto")

# Agregar carpetas de datos
if os.path.exists("assets"):
    cmd.append("--add-data=assets;assets")
    print("   ✓ Incluyendo: assets/")
if os.path.exists("imagenes"):
    cmd.append("--add-data=imagenes;imagenes")
    print("   ✓ Incluyendo: imagenes/")

# Agregar hooks y opciones
cmd.extend([
    # Hooks para CustomTkinter
    "--collect-all=customtkinter",
    "--copy-metadata=customtkinter",
    
    # Hooks para Matplotlib
    "--collect-all=matplotlib",
    "--copy-metadata=matplotlib",
    
    # Hooks para otros paquetes
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=numpy",
    "--hidden-import=numpy.core._methods",
    "--hidden-import=numpy.lib.format",
    "--hidden-import=roboticstoolbox",
    "--hidden-import=spatialmath",
    "--hidden-import=cartopy",
    "--hidden-import=pandas",
    "--hidden-import=serial",
    "--hidden-import=queue",
    
    # Agregar módulos del proyecto
    "--hidden-import=ComSerial",
    "--hidden-import=GPS",
    "--hidden-import=CargaSensor",
    "--hidden-import=Interpretacion",
    "--hidden-import=CTkXYFrame",
    
    # Opciones adicionales
    "--noconfirm",
    "--clean",
    
    # Archivo principal
    "run.py"
])

print()
print("   Iniciando PyInstaller...")
print()

try:
    # Ejecutar PyInstaller
    result = subprocess.run(cmd, check=True, text=True)
    
    print()
    print("=" * 70)
    print("✅ EJECUTABLE CREADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print(f"📁 Ubicación: {os.path.abspath('dist/SoftwareRadar.exe')}")
    
    # Obtener tamaño del ejecutable
    exe_path = Path("dist/SoftwareRadar.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"📊 Tamaño: {size_mb:.1f} MB")
    
    print()
    print("📋 NOTAS IMPORTANTES:")
    print("   1. El ejecutable está en la carpeta 'dist/'")
    print("   2. Puedes distribuir solo el archivo .exe")
    print("   3. NO necesitas Python instalado en la PC destino")
    print("   4. Asegúrate de incluir archivos de datos (CSV) si es necesario")
    print()
    print("🧪 Para probar el ejecutable:")
    print("   cd dist")
    print("   .\\SoftwareRadar.exe")
    print()
    
except subprocess.CalledProcessError as e:
    print()
    print("=" * 70)
    print("❌ ERROR AL CREAR EJECUTABLE")
    print("=" * 70)
    print()
    print("💡 Posibles soluciones:")
    print("   1. Verifica que todas las dependencias estén instaladas:")
    print("      pip install -r requirements.txt")
    print("   2. Revisa que los archivos de recursos existan")
    print("   3. Consulta el archivo BUILD_EXECUTABLE.md para más ayuda")
    print()
    sys.exit(1)
except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERROR INESPERADO")
    print("=" * 70)
    print()
    print(f"Error: {e}")
    print()
    print("💡 Intenta ejecutar manualmente:")
    print(f"   {sys.executable} -m PyInstaller --onefile --windowed run.py")
    print()
    sys.exit(1)
