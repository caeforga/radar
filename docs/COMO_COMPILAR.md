# 🚀 Cómo Compilar Software Radar - GUÍA RÁPIDA

## ⚡ 3 Métodos (de más fácil a más avanzado)

---

### **Método 1: Super Simple (Recomendado si tienes problemas)**

```bash
build_simple.bat
```

✅ **Ventajas:**
- Configuración mínima
- Más compatible
- Ve el progreso en tiempo real
- Solo incluye lo esencial

---

### **Método 2: Script Python Completo**

```bash
python build_exe.py
```

✅ **Ventajas:**
- Incluye todas las características
- Manejo robusto de errores
- Reportes detallados

---

### **Método 3: Comando Manual (Para expertos)**

```bash
python -m PyInstaller --name=SoftwareRadar --onefile --windowed run.py
```

✅ **Ventajas:**
- Control total
- Más rápido
- Personalizable

---

## 🎯 ¿Cuál usar?

| Situación | Método Recomendado |
|-----------|-------------------|
| **Primera vez compilando** | `build_simple.bat` |
| **Tuviste errores antes** | `build_simple.bat` |
| **Quieres todas las funciones** | `python build_exe.py` |
| **Sabes lo que haces** | Comando manual |

---

## 📦 Resultado

Todos crean el mismo resultado:

```
dist/
└── SoftwareRadar.exe    (150-300 MB)
```

---

## ⏱️ Tiempo de Compilación

- **Primera vez**: 8-12 minutos
- **Compilaciones siguientes**: 5-8 minutos

---

## ✅ Pasos Después de Compilar

1. **Probar en tu PC:**
   ```bash
   cd dist
   .\SoftwareRadar.exe
   ```

2. **Probar en otra PC** (sin Python)

3. **Distribuir** el archivo .exe

---

## 🐛 Si Hay Errores

### Error: "No module named PyInstaller"
```bash
python -m pip install pyinstaller
```

### Error: "No module named XXX"
```bash
pip install -r requirements.txt
```

### Error: Antivirus bloquea
- Agregar excepción para el ejecutable
- Es normal, el código es seguro

---

## 💡 Consejo

**Si `build.bat` no funciona, usa `build_simple.bat`**

Es más directo y tiene menos problemas.

---

## 📚 Documentación Completa

Para más detalles: `BUILD_EXECUTABLE.md`

---

**¡Listo para compilar! Elige un método y ejecuta.** 🎉

