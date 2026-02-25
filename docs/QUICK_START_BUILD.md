# 🚀 Guía Rápida - Compilar a Ejecutable

## ⚡ Método Ultra-Rápido

### **Opción 1: Script Batch (Windows)**

```bash
build.bat
```

¡Eso es todo! El script hace todo automáticamente.

---

### **Opción 2: Script Python**

```bash
python build_exe.py
```

---

### **Opción 3: PyInstaller Directo**

```bash
pyinstaller SoftwareRadar.spec
```

---

## 📦 Resultado

Después de ~5-10 minutos:

```
dist/
└── SoftwareRadar.exe    ⭐ Tu ejecutable (150-300 MB)
```

---

## 🧪 Probar

```bash
cd dist
.\SoftwareRadar.exe
```

O simplemente haz doble clic en el archivo.

---

## 📤 Distribuir

**Opción A: Solo el ejecutable**
- Copia `SoftwareRadar.exe` a cualquier PC con Windows
- No necesita Python ni dependencias
- ¡Funciona directamente!

**Opción B: Con datos**
```
📦 SoftwareRadar_v1.0.zip
├── SoftwareRadar.exe
├── CR310_RK900_10.csv (opcional)
└── README_EJECUTABLE.md
```

---

## ⚠️ Problemas Comunes

### PyInstaller no instalado
```bash
pip install pyinstaller
```

### Error "module not found"
```bash
pip install -r requirements.txt
```

### Antivirus bloquea el .exe
- Es normal con ejecutables nuevos
- Agrega excepción en tu antivirus
- El código es seguro (open source)

---

## 📚 Documentación Completa

Para configuración avanzada, troubleshooting y opciones:

👉 **[BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md)**

---

## ✅ Checklist

Antes de distribuir:

- [ ] Ejecutable se abre sin errores
- [ ] Probado en PC sin Python
- [ ] Todos los paneles funcionan
- [ ] Conexión serial OK
- [ ] Gráficos se muestran correctamente
- [ ] Incluido README para usuarios

---

## 🎯 Resumen

| Método | Comando | Tiempo | Dificultad |
|--------|---------|--------|------------|
| **Batch** | `build.bat` | 5-10 min | ⭐ Muy Fácil |
| **Python** | `python build_exe.py` | 5-10 min | ⭐ Fácil |
| **PyInstaller** | `pyinstaller SoftwareRadar.spec` | 5-10 min | ⭐⭐ Fácil |

---

¡Listo para distribuir! 🎉

