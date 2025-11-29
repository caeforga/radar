# 📦 Guía de Compilación a Ejecutable - Software Radar

## 🎯 Objetivo

Crear un ejecutable independiente de **Software Radar** que pueda ejecutarse en cualquier PC con Windows sin necesidad de tener Python instalado.

---

## 🛠️ Herramientas Utilizadas

### **PyInstaller**
PyInstaller es la herramienta elegida porque:
- ✅ Soporta aplicaciones GUI complejas
- ✅ Maneja bien CustomTkinter y Matplotlib
- ✅ Crea ejecutables de un solo archivo
- ✅ Incluye todas las dependencias automáticamente
- ✅ No requiere instalación en la PC destino

---

## 📋 Requisitos Previos

### 1. **Python y Dependencias**
Asegúrate de tener todo instalado:

```bash
# Verificar versión de Python
python --version

# Instalar/verificar dependencias del proyecto
pip install -r requirements.txt

# Instalar PyInstaller
pip install pyinstaller
```

### 2. **Entorno Virtual Limpio (Recomendado)**
Para un ejecutable más pequeño y sin dependencias innecesarias:

```bash
# Crear entorno virtual limpio
python -m venv venv_build

# Activar entorno
venv_build\Scripts\activate

# Instalar solo lo necesario
pip install -r requirements.txt
pip install pyinstaller
```

---

## 🚀 Método 1: Script Automático (Recomendado)

### **Opción A: Script Python**

```bash
python build_exe.py
```

Este script automáticamente:
1. ✅ Limpia builds anteriores
2. ✅ Verifica e instala PyInstaller si es necesario
3. ✅ Configura todos los parámetros correctos
4. ✅ Crea el ejecutable en `dist/SoftwareRadar.exe`
5. ✅ Muestra el tamaño y ubicación del ejecutable

### **Opción B: Usando el archivo .spec**

```bash
pyinstaller SoftwareRadar.spec
```

Usa el archivo de especificación predefinido con todas las configuraciones optimizadas.

---

## 🔧 Método 2: Comando Manual

Si prefieres tener control total:

```bash
pyinstaller ^
  --name=SoftwareRadar ^
  --onefile ^
  --windowed ^
  --icon=assets/images/Icono radar.png ^
  --add-data=assets;assets ^
  --add-data=imagenes;imagenes ^
  --collect-all=customtkinter ^
  --collect-all=matplotlib ^
  --hidden-import=roboticstoolbox ^
  --hidden-import=numpy ^
  --hidden-import=PIL ^
  --hidden-import=serial ^
  --hidden-import=cartopy ^
  --noconfirm ^
  --clean ^
  run.py
```

### **Explicación de parámetros:**

| Parámetro | Descripción |
|-----------|-------------|
| `--name=SoftwareRadar` | Nombre del ejecutable |
| `--onefile` | Un solo archivo .exe (no carpeta) |
| `--windowed` | Sin ventana de consola (GUI only) |
| `--icon=...` | Icono del ejecutable |
| `--add-data=...` | Incluir archivos de recursos |
| `--collect-all=...` | Recopilar todos los archivos de un paquete |
| `--hidden-import=...` | Importaciones que PyInstaller no detecta |
| `--noconfirm` | Sobrescribir sin preguntar |
| `--clean` | Limpiar cache antes de construir |

---

## 📁 Estructura Después de la Compilación

```
SoftwareRadar-main/
├── build/                      # Archivos temporales (se puede borrar)
├── dist/                       # 📦 EJECUTABLE AQUÍ
│   └── SoftwareRadar.exe       # ⭐ Tu ejecutable
├── SoftwareRadar.spec          # Archivo de configuración
└── build_exe.py                # Script de construcción
```

---

## 🧪 Probar el Ejecutable

### **En tu PC (desarrollo):**

```bash
cd dist
.\SoftwareRadar.exe
```

### **En otra PC (producción):**

1. Copia `SoftwareRadar.exe` a la PC destino
2. Haz doble clic para ejecutar
3. **NO se requiere Python ni ninguna dependencia**

---

## 📦 Distribución

### **Opción 1: Ejecutable Solo**
Si **NO** necesitas archivos externos (CSV, configuración, etc.):
- ✅ Distribuye solo `SoftwareRadar.exe`
- ✅ Tamaño: ~150-300 MB (incluye todo)

### **Opción 2: Ejecutable + Datos**
Si necesitas archivos externos:

```
📦 SoftwareRadar_v1.0.zip
├── SoftwareRadar.exe           # Ejecutable
├── data/                       # Datos opcionales
│   └── CR310_RK900_10.csv      # Sensor data
├── config/                     # Configuración opcional
└── README_Usuario.txt          # Instrucciones
```

---

## ⚙️ Configuración Avanzada

### **1. Reducir Tamaño del Ejecutable**

#### **A. Excluir paquetes innecesarios**
Edita `SoftwareRadar.spec`:

```python
excludes=[
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'sphinx',
    'tkinter.test',
    'unittest',
]
```

#### **B. Comprimir con UPX**
UPX reduce el tamaño del ejecutable:

```bash
# Descargar UPX desde: https://upx.github.io/
# Extraer en una carpeta y agregar al PATH

# Compilar con UPX habilitado
pyinstaller --upx-dir=C:\path\to\upx SoftwareRadar.spec
```

### **2. Agregar Ventana de Consola (Debug)**

Para ver mensajes de error durante desarrollo:

```python
# En SoftwareRadar.spec, cambiar:
console=True  # En lugar de False
```

O en comando manual:
```bash
# Remover --windowed
pyinstaller --onefile run.py
```

### **3. Múltiples Archivos (Más Rápido de Iniciar)**

En lugar de `--onefile`, usa `--onedir`:

```bash
pyinstaller --onedir --windowed run.py
```

**Resultado:**
```
dist/
└── SoftwareRadar/              # Carpeta con todo
    ├── SoftwareRadar.exe       # Ejecutable
    └── _internal/              # DLLs y dependencias
```

**Ventajas:**
- ✅ Inicia más rápido
- ✅ Más fácil de debuggear

**Desventajas:**
- ❌ Muchos archivos para distribuir
- ❌ Más confuso para usuarios

---

## 🐛 Solución de Problemas

### **Error: "No module named 'customtkinter'"**

**Solución:**
```bash
pyinstaller --collect-all customtkinter --copy-metadata customtkinter run.py
```

### **Error: "No module named 'roboticstoolbox'"**

**Solución:**
```bash
pip install roboticstoolbox-python
pyinstaller --hidden-import=roboticstoolbox --collect-all=roboticstoolbox run.py
```

### **Error: Matplotlib no muestra gráficos**

**Solución:**
```python
# En SoftwareRadar.spec, agregar:
hiddenimports=[
    'matplotlib.backends.backend_tkagg',
    'matplotlib.figure',
]
```

### **Error: "Failed to execute script"**

**Causas comunes:**
1. ❌ Falta un módulo oculto
2. ❌ Archivo de datos no incluido
3. ❌ Error en el código

**Solución:**
1. Compilar con consola habilitada (`console=True`)
2. Ejecutar desde CMD para ver errores:
   ```bash
   cd dist
   SoftwareRadar.exe
   ```
3. Agregar imports faltantes en `.spec`

### **Ejecutable muy grande (>500 MB)**

**Soluciones:**

1. **Usar entorno virtual limpio:**
   ```bash
   python -m venv venv_clean
   venv_clean\Scripts\activate
   pip install SOLO_LO_NECESARIO
   ```

2. **Excluir paquetes grandes innecesarios:**
   ```python
   excludes=['scipy.spatial.cKDTree', ...]
   ```

3. **Usar UPX para comprimir:**
   ```bash
   pyinstaller --upx-dir=path/to/upx SoftwareRadar.spec
   ```

### **Error: "Cannot find existing PyQt5 plugin directories"**

Si no usas PyQt5:
```python
excludes=['PyQt5']
```

---

## 📊 Checklist de Compilación

Antes de distribuir el ejecutable:

### **Testing:**
- [ ] Ejecutable se abre sin errores
- [ ] Conexión serial funciona
- [ ] Panel de control muestra robot 3D
- [ ] Panel de visualización muestra gráficos
- [ ] Sliders funcionan correctamente
- [ ] Botones responden
- [ ] No hay crashes al cambiar de panel

### **Distribución:**
- [ ] Ejecutable probado en PC limpia (sin Python)
- [ ] Incluir README con instrucciones
- [ ] Documentar requisitos mínimos del sistema
- [ ] Crear archivo de licencia si es necesario
- [ ] Versionar el ejecutable (v1.0, v1.1, etc.)

### **Requisitos del Sistema (para el README):**
```
Sistema Operativo: Windows 10/11 (64-bit)
RAM: 4 GB mínimo (8 GB recomendado)
Espacio en disco: 500 MB
Puerto COM disponible (para conexión con hardware)
```

---

## 🎨 Personalización

### **1. Cambiar Icono del Ejecutable**

```bash
# Asegúrate de tener un archivo .ico
# Puedes convertir .png a .ico en: https://convertio.co/png-ico/

pyinstaller --icon=mi_icono.ico run.py
```

### **2. Agregar Información de Versión (Windows)**

Crea `version_info.txt`:

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Tu Empresa'),
        StringStruct(u'FileDescription', u'Software Radar'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'SoftwareRadar'),
        StringStruct(u'ProductName', u'Software Radar'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

Luego:
```bash
pyinstaller --version-file=version_info.txt run.py
```

---

## 📚 Recursos Adicionales

- [Documentación de PyInstaller](https://pyinstaller.org/en/stable/)
- [PyInstaller con CustomTkinter](https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging)
- [UPX Compressor](https://upx.github.io/)
- [Auto-py-to-exe (GUI para PyInstaller)](https://github.com/brentvollebregt/auto-py-to-exe)

---

## 🚀 Método Alternativo: Auto-py-to-exe (GUI)

Si prefieres una interfaz gráfica:

```bash
# Instalar
pip install auto-py-to-exe

# Ejecutar GUI
auto-py-to-exe
```

**Configuración en la GUI:**
1. Script Location: `run.py`
2. One File: ✅
3. Window Based: ✅
4. Icon: Seleccionar `assets/images/Icono radar.png`
5. Additional Files: Agregar carpetas `assets` e `imagenes`
6. Hidden Imports: Agregar todos los listados arriba
7. Click "CONVERT .PY TO .EXE"

---

## 🎯 Recomendación Final

**Para la mayoría de usuarios:**
```bash
python build_exe.py
```

Este script automático maneja todo el proceso y crea un ejecutable optimizado listo para distribuir.

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** en `build/` después de compilar
2. **Habilita consola** (`console=True`) para ver errores
3. **Verifica hiddenimports** si falta algún módulo
4. **Consulta** [PyInstaller Documentation](https://pyinstaller.org/en/stable/)

---

**Última actualización:** Noviembre 2025  
**Versión de PyInstaller recomendada:** 6.0+  
**Python compatible:** 3.8 - 3.11

