# Cómo Compilar Software Radar

## Requisitos Previos

- **Python 3.x** instalado
- Dependencias del proyecto instaladas:
  ```bash
  pip install -r requirements.txt
  ```
- **PyInstaller** (se instala automáticamente si no lo tienes)

---

## Compilar el Ejecutable

Desde la raíz del proyecto, ejecuta:

```bash
python build_exe.py
```

El script se encarga de todo automáticamente:

1. Verifica que estés en el directorio correcto
2. Limpia builds anteriores (`build/`, `dist/`, `__pycache__/`, archivos `.spec`)
3. Instala PyInstaller si no está disponible
4. Detecta e incluye el icono del proyecto si existe
5. Incluye las carpetas de recursos (`assets/`, `imagenes/`)
6. Empaqueta todas las dependencias necesarias (CustomTkinter, Matplotlib, NumPy, Cartopy, etc.)
7. Genera un ejecutable único con `--onefile --windowed`

---

## Resultado

```
dist/
└── SoftwareRadar.exe
```

El ejecutable no requiere Python instalado en la PC destino.

---

## Estructura de Datos para el Ejecutable

Para usar archivos CSV de lecturas del radar, crea esta estructura junto al `.exe`:

```
SoftwareRadar.exe
└── output/
    └── Lecturas RADAR/
        └── tu_archivo.csv
```

La aplicación crea estas carpetas automáticamente si no existen. Si no hay archivos CSV, puedes usar el modo DEMO en el panel de mapa.

---

## Tiempo de Compilación

- **Primera vez**: 8-12 minutos
- **Compilaciones siguientes**: 5-8 minutos

---

## Probar el Ejecutable

```bash
cd dist
.\SoftwareRadar.exe
```

---

## Solución de Errores

### "No module named PyInstaller"
```bash
pip install pyinstaller
```

### "No module named XXX"
```bash
pip install -r requirements.txt
```

### El antivirus bloquea el ejecutable
Agrega una excepción para el archivo. Es un falso positivo común con ejecutables generados por PyInstaller.

### Error inesperado
Intenta compilar manualmente para ver el error detallado:
```bash
python -m PyInstaller --onefile --windowed run.py
```
