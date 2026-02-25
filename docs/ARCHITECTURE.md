# 🏗️ Arquitectura del Proyecto - Software Radar

Este documento describe la arquitectura y estructura del proyecto Software Radar.

---

## 📁 Estructura del Proyecto

```
SoftwareRadar/
├── src/                           # Código fuente principal
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada de la aplicación
│   │
│   ├── config/                    # Configuración
│   │   ├── __init__.py
│   │   └── settings.py            # Configuración global del sistema
│   │
│   ├── core/                      # Lógica de negocio core
│   │   ├── __init__.py
│   │   │
│   │   ├── communication/         # Módulos de comunicación
│   │   │   ├── __init__.py
│   │   │   └── serial_comm.py     # Comunicación serial (refactorizado de ComSerial.py)
│   │   │
│   │   ├── hardware/              # Interfaces de hardware
│   │   │   ├── __init__.py
│   │   │   ├── gps.py             # Parser GPS NMEA (refactorizado de GPS.py)
│   │   │   ├── sensor.py          # Sensor meteorológico (refactorizado de CargaSensor.py)
│   │   │   └── motors.py          # Control de motores (refactorizado de ControlMotores.py)
│   │   │
│   │   └── data/                  # Procesamiento de datos
│   │       ├── __init__.py
│   │       ├── capture.py         # Captura de datos (Captura.py)
│   │       └── interpretation.py  # Interpretación de datos del radar (Interpretacion.py)
│   │
│   ├── ui/                        # Interfaz gráfica
│   │   ├── __init__.py
│   │   ├── app.py                 # Aplicación principal (refactorizado de mejorada.py)
│   │   │
│   │   ├── components/            # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   └── xy_frame.py        # Frame XY personalizado (CTkXYFrame)
│   │   │
│   │   ├── panels/                # Paneles de la interfaz
│   │   │   ├── __init__.py
│   │   │   ├── control_panel.py   # Panel de control
│   │   │   └── visualization_panel.py  # Panel de visualización
│   │   │
│   │   └── widgets/               # Widgets especializados
│   │       ├── __init__.py
│   │       └── graphics.py        # Gráficos del radar (GraficoObject.py)
│   │
│   └── utils/                     # Utilidades
│       ├── __init__.py
│       └── helpers.py             # Funciones auxiliares
│
├── assets/                        # Recursos estáticos
│   └── images/                    # Imágenes de la interfaz
│       ├── Icono radar.png
│       ├── Icono palanca.png
│       └── Icono fac.png
│
├── data/                          # Datos del sistema
│   ├── output/                    # Datos de salida
│   │   ├── lecturas_radar/        # Lecturas del radar (CSV)
│   │   └── raw_data/              # Datos crudos (.sal)
│   └── sensors/                   # Datos de sensores
│       └── CR310_RK900_10.csv     # Datos del sensor meteorológico
│
├── firmware/                      # Firmware de dispositivos
│   ├── esp32/                     # Firmware ESP32
│   │   ├── FirmwareESP32.ino
│   │   └── FirmwareESP32Optimizado.ino
│   └── brujula/                   # Firmware brújula
│       └── Brujula.ino
│
├── hardware/                      # Diseños de hardware
│   └── pcb/                       # Diseños PCB (KiCad)
│       └── [archivos de PCB FINAL]
│
├── tests/                         # Tests unitarios e integración
│   └── [archivos de test]
│
├── docs/                          # Documentación adicional
│   └── [documentos]
│
├── requirements.txt               # Dependencias Python
├── README.md                      # Documentación principal
├── ARCHITECTURE.md                # Este archivo
├── GIT_GUIDE.md                   # Guía de uso de Git
├── .gitignore                     # Archivos ignorados por Git
└── .gitattributes                 # Atributos de Git

```

---

## 🎯 Principios de Diseño

### 1. **Separación de Concerns (SoC)**
Cada módulo tiene una responsabilidad única y bien definida:
- **`core/`**: Lógica de negocio sin dependencias de UI
- **`ui/`**: Interfaz gráfica sin lógica de negocio compleja
- **`config/`**: Configuración centralizada

### 2. **Inyección de Dependencias**
Los módulos reciben sus dependencias en lugar de crearlas internamente, facilitando testing y mantenimiento.

### 3. **Modularidad**
Cada componente puede ser desarrollado, probado y mantenido independientemente.

### 4. **Compatibilidad hacia atrás**
Los módulos refactorizados mantienen funciones legacy para no romper código existente.

---

## 🔄 Flujo de Datos

```
┌─────────────┐
│   Hardware  │
│  (Radar,    │
│  GPS, etc.) │
└──────┬──────┘
       │
       ↓ Serial
┌─────────────────────────────┐
│ core/communication/         │
│ serial_comm.py              │
└──────┬──────────────────────┘
       │
       ↓
┌─────────────────────────────┐
│ core/hardware/              │
│ gps.py, sensor.py           │
└──────┬──────────────────────┘
       │
       ↓
┌─────────────────────────────┐
│ core/data/                  │
│ interpretation.py           │
└──────┬──────────────────────┘
       │
       ↓
┌─────────────────────────────┐
│ ui/                         │
│ app.py, panels/, widgets/   │
└──────┬──────────────────────┘
       │
       ↓
┌─────────────────────────────┐
│      Usuario                │
└─────────────────────────────┘
```

---

## 📦 Módulos Principales

### `src/config/settings.py`
- Configuración global del sistema
- Constantes y rutas
- Singleton para acceso global

### `src/core/communication/serial_comm.py`
- Gestión de comunicación serial
- Thread-safe
- Context manager support

### `src/core/hardware/`
- **`gps.py`**: Parser NMEA para GPS
- **`sensor.py`**: Lectura de sensores meteorológicos
- **`motors.py`**: Control de motores del radar

### `src/core/data/`
- **`interpretation.py`**: Interpretación de datos del radar
- **`capture.py`**: Captura de datos con Logic Analyzer

### `src/ui/`
- **`app.py`**: Aplicación principal CustomTkinter
- **`panels/`**: Paneles de control y visualización
- **`widgets/`**: Widgets especializados (gráficos radar)
- **`components/`**: Componentes reutilizables

---

## 🔌 API Principal

### SerialCommunication
```python
from src.core.communication import SerialCommunication

# Uso moderno
comm = SerialCommunication(timeout=0.5)
comm.get_available_ports()
comm.connect()
comm.send_data("comando")
data = comm.read_data()
comm.disconnect()

# O con context manager
with SerialCommunication() as comm:
    comm.connect()
    comm.send_data("comando")
```

### GPSParser
```python
from src.core.hardware import GPSParser

# Parsear trama NMEA
data = GPSParser.parse_nmea("$GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47")
print(data['latitude'], data['longitude'])
```

### WeatherSensor
```python
from src.core.hardware import WeatherSensor

sensor = WeatherSensor("data/sensors/CR310_RK900_10.csv")
reading = sensor.get_last_reading()
temp = sensor.get_temperature()
wind = sensor.get_wind_direction()
```

---

## 🧪 Testing

### Estructura de Tests
```
tests/
├── __init__.py
├── test_communication/
│   └── test_serial_comm.py
├── test_hardware/
│   ├── test_gps.py
│   └── test_sensor.py
└── test_ui/
    └── test_app.py
```

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_hardware/test_gps.py

# Con cobertura
pytest --cov=src tests/
```

---

## 📝 Guías de Estilo

### Python
- **PEP 8**: Estilo de código Python
- **Type Hints**: Usar anotaciones de tipo
- **Docstrings**: Google style o NumPy style
- **Logging**: Usar módulo logging en lugar de print

### Naming Conventions
- **Clases**: `PascalCase` (ej: `SerialCommunication`)
- **Funciones/Métodos**: `snake_case` (ej: `get_available_ports`)
- **Constantes**: `UPPER_SNAKE_CASE` (ej: `DEFAULT_BAUDRATE`)
- **Privados**: `_leading_underscore` (ej: `_parse_data`)

---

## 🔧 Mantenimiento

### Agregar Nuevo Hardware
1. Crear módulo en `src/core/hardware/`
2. Implementar interfaz consistente
3. Añadir a `__init__.py`
4. Documentar en README
5. Añadir tests

### Agregar Nuevo Panel UI
1. Crear archivo en `src/ui/panels/`
2. Heredar de CTkFrame
3. Implementar interfaz consistente
4. Integrar en `app.py`
5. Añadir assets si es necesario

---

## 🚀 Migración desde Código Legacy

### Imports Antiguos → Nuevos

```python
# Antes
from ComSerial import comunicacion
from GPS import parse_nmea
import CargaSensor as CS

# Después
from src.core.communication import SerialCommunication
from src.core.hardware import GPSParser, WeatherSensor

# O mantener compatibilidad
from src.core.communication.serial_comm import comunicacion  # alias legacy
from src.core.hardware.gps import parse_nmea  # función legacy
from src.core.hardware.sensor import obtener_ultima_lectura  # función legacy
```

---

## 📚 Referencias

- [Python Best Practices](https://docs.python-guide.org/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Versión de la arquitectura**: 2.0
**Última actualización**: 2025-01-12

