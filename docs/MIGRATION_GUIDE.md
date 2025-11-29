# 📘 Guía de Migración - Software Radar v2.0

Esta guía te ayudará a migrar tu código desde la estructura anterior a la nueva arquitectura.

---

## 🔄 Cambios Principales

### Estructura de Carpetas

| Antes | Después |
|-------|---------|
| `ComSerial.py` | `src/core/communication/serial_comm.py` |
| `GPS.py` | `src/core/hardware/gps.py` |
| `CargaSensor.py` | `src/core/hardware/sensor.py` |
| `ControlMotores.py` | `src/core/hardware/motors.py` |
| `Interpretacion.py` | `src/core/data/interpretation.py` |
| `Captura.py` | `src/core/data/capture.py` |
| `mejorada.py` | `src/ui/app.py` |
| `GraficoObject.py` | `src/ui/widgets/graphics.py` |
| `CTkXYFrame/` | `src/ui/components/` |
| `imagenes/` | `assets/images/` |
| `output/` | `data/output/` |

---

## 📝 Migración de Imports

### Comunicación Serial

```python
# ❌ Antes
from ComSerial import comunicacion
serial = comunicacion()

# ✅ Ahora (recomendado)
from src.core.communication import SerialCommunication
serial = SerialCommunication()

# ✅ O mantener compatibilidad
from src.core.communication.serial_comm import comunicacion
serial = comunicacion()
```

### GPS

```python
# ❌ Antes
import GPS
data = GPS.main(sentence)

# ✅ Ahora (recomendado)
from src.core.hardware import GPSParser
data = GPSParser.parse_nmea(sentence)

# ✅ O mantener compatibilidad
from src.core.hardware.gps import main
data = main(sentence)
```

### Sensor Meteorológico

```python
# ❌ Antes
import CargaSensor as CS
lectura = CS.obtener_ultima_lectura("archivo.csv")

# ✅ Ahora (recomendado)
from src.core.hardware import WeatherSensor
sensor = WeatherSensor("archivo.csv")
lectura = sensor.get_last_reading()

# ✅ O mantener compatibilidad
from src.core.hardware.sensor import obtener_ultima_lectura
lectura = obtener_ultima_lectura("archivo.csv")
```

---

## 🎨 Migración de UI

### Aplicación Principal

```python
# ❌ Antes
from mejorada import App
app = App()

# ✅ Ahora
from src.ui.app import RadarApp
app = RadarApp()
app.run()
```

### Componentes

```python
# ❌ Antes
from CTkXYFrame import CTkXYFrame

# ✅ Ahora
from src.ui.components import CTkXYFrame
```

---

## 🔧 Configuración

### Configuración Global

```python
# ✅ Nuevo
from src.config import Settings

settings = Settings()
print(settings.window_width)
print(settings.default_baudrate)
```

---

## 🚀 Ejecución

### Antes
```bash
python mejorada.py
```

### Ahora
```bash
python run.py
# O
python -m src.main
```

---

## ⚠️ Breaking Changes

1. **Nombres de Clases**: Algunas clases han sido renombradas para seguir convenciones PEP 8
   - `comunicacion` → `SerialCommunication`
   
2. **Rutas de Assets**: Las imágenes ahora están en `assets/images/`
   
3. **Datos de Salida**: Ahora se guardan en `data/output/`

---

## 🔄 Pasos de Migración

### 1. Actualizar Imports

Busca y reemplaza los imports en tu código:

```bash
# Buscar archivos que usan imports antiguos
grep -r "from ComSerial" .
grep -r "import GPS" .
grep -r "import CargaSensor" .
```

### 2. Actualizar Rutas

Si tienes código que accede a rutas directamente:

```python
# ❌ Antes
imagen = "imagenes/Icono radar.png"

# ✅ Ahora
from src.config import Settings
settings = Settings()
imagen = settings.ICON_RADAR
```

### 3. Probar

Ejecuta tu código y verifica que todo funciona:

```bash
python run.py
```

---

## 💡 Ventajas de la Nueva Estructura

1. ✅ **Modularidad**: Código más organizado y fácil de mantener
2. ✅ **Testing**: Más fácil escribir tests unitarios
3. ✅ **Escalabilidad**: Estructura preparada para crecimiento
4. ✅ **Documentación**: Mejor documentada con docstrings
5. ✅ **Type Hints**: Anotaciones de tipo para mejor IDE support
6. ✅ **Logging**: Sistema de logging estructurado

---

## 🆘 Problemas Comunes

### Error: "No module named 'src'"

**Solución**: Ejecuta desde la raíz del proyecto:
```bash
cd SoftwareRadar
python run.py
```

### Error: "FileNotFoundError" para imágenes

**Solución**: Las imágenes ahora están en `assets/images/`. Usa la configuración:
```python
from src.config.settings import ICON_RADAR
```

### Error de imports circulares

**Solución**: La nueva estructura evita esto. Si lo encuentras, revisa tus imports.

---

## 📚 Recursos Adicionales

- [ARCHITECTURE.md](../ARCHITECTURE.md): Arquitectura completa del proyecto
- [README.md](../README.md): Documentación actualizada
- [GIT_GUIDE.md](../GIT_GUIDE.md): Guía de uso de Git

---

**¿Necesitas ayuda con la migración?** Abre un issue en GitHub.

