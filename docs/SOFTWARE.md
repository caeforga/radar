# Software Radar v2.0

Sistema de control y visualización para radar meteorológico con arquitectura modular.

---

## Características

- Control de motores de rotación e inclinación con visualización 3D del robot
- Visualización en tiempo real de datos del radar en gráficos polares
- Integración GPS con captura de coordenadas y orientación
- Monitoreo de datos meteorológicos (temperatura, viento, humedad, presión, precipitación)
- Panel de mapa geográfico interactivo con overlay del radar
- Configuración de ganancia, rango, modos de operación y tracking
- Registro automático de lecturas en CSV
- UI responsiva que se adapta a cualquier resolución de pantalla
- Compilable a ejecutable independiente (no requiere Python en la PC destino)

---

## Requisitos

- **Python 3.12** o superior
- Dependencias: `pip install -r requirements.txt`
- Puerto serial para conexión con hardware (COM)
- Windows 10/11 (64-bit)

---

## Ejecución

```bash
python run.py
```

Alternativa como módulo:

```bash
python -m src.main
```

---

## Estructura del Proyecto

```
SoftwareRadar/
├── src/
│   ├── config/settings.py                # Configuración centralizada
│   ├── core/
│   │   ├── communication/serial_comm.py  # Comunicación serial
│   │   ├── hardware/gps.py              # Parser GPS NMEA
│   │   ├── hardware/sensor.py           # Sensor meteorológico
│   │   ├── hardware/motors.py           # Control de motores
│   │   └── data/interpretation.py       # Interpretación de datos del radar
│   ├── ui/
│   │   ├── app_responsive.py            # Aplicación principal
│   │   └── panels/
│   │       ├── control_panel_responsive.py
│   │       ├── visualization_panel_responsive.py
│   │       └── map_panel_responsive.py
│   └── main.py
├── assets/images/                        # Iconos e imágenes
├── firmware/                             # Firmware ESP32 y brújula
├── hardware/pcb/                         # Diseños PCB (KiCad)
├── docs/                                 # Documentación
├── run.py                                # Punto de entrada
└── requirements.txt
```

---

## Flujo de Datos

```
Hardware (Radar, GPS, Sensores)
        │ Serial
        ▼
  SerialCommunication
        │
        ▼
  GPSParser / WeatherSensor / Interpretation
        │
        ▼
  UI (Paneles de Control, Visualización, Mapa)
        │
        ▼
     Usuario
```

---

## Paneles de la Aplicación

### Panel de Control

Gestiona la conexión serial y el control del hardware.

- **Conexión serial**: Selección de puerto COM y baud rate, botones de conectar/desconectar/actualizar
- **Robot 3D**: Visualización del modelo cinemático en tiempo real
- **Sliders**: Motor de rotación (-180° a +180°) y motor de inclinación (-60° a +60°)
- **Modos de operación**: Apagar, Standby, TEST, ON
- **Controles avanzados**: Ajuste de inclinación, ganancia, RNG (rango), VP (perfil vertical), TRK (tracking)

### Panel de Visualización

Muestra los datos del radar en tiempo real.

- **Gráfico polar**: Visualización de detecciones con colores por intensidad
- **Indicadores**: Aceptación, modo de operación, fallos, modos especiales
- **Parámetros**: Rango, ganancia, inclinación, track
- **Sensores meteorológicos**: Temperatura, humedad, presión, velocidad/dirección del viento, precipitación
- **GPS y brújula**: Coordenadas y orientación en tiempo real
- **Actualización automática** cada segundo

### Panel de Mapa

Vista geográfica interactiva con la posición del radar.

- **Mapa interactivo** con tiles de OpenStreetMap, Google Maps (satélite, calles, terreno, híbrido)
- **Marker del radar** con actualización GPS en tiempo real
- **Círculos de rango** concéntricos (25, 50, 75 km + rango configurado)
- **Sector de cobertura** con apertura de 90° según la orientación de la brújula
- **Leyenda dBZ** con escala de colores de reflectividad
- **Overlays**: Ubicación (lat/lon/orientación), parámetros (rango/ganancia/operación), estado de aceptación
- Requiere: `pip install tkintermapview`

---

## API de Módulos

### SerialCommunication

```python
from src.core.communication import SerialCommunication

comm = SerialCommunication()
comm.get_available_ports()
comm.arduino.port = "COM3"
comm.connect()
comm.send_data("comando")
comm.disconnect()
```

### GPSParser

```python
from src.core.hardware import GPSParser

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

### Settings

```python
from src.config import Settings

settings = Settings()
print(settings.window_width)
print(settings.default_baudrate)
print(settings.ICON_RADAR)
```

---

## Migración desde v1.x

Los módulos refactorizados mantienen aliases de compatibilidad:

```python
# Legacy (sigue funcionando)
from src.core.communication.serial_comm import comunicacion
from src.core.hardware.gps import parse_nmea, main
from src.core.hardware.sensor import obtener_ultima_lectura

# Recomendado
from src.core.communication import SerialCommunication
from src.core.hardware import GPSParser, WeatherSensor
```

Rutas de archivos actualizadas:

| Antes | Ahora |
|-------|-------|
| `ComSerial.py` | `src/core/communication/serial_comm.py` |
| `GPS.py` | `src/core/hardware/gps.py` |
| `CargaSensor.py` | `src/core/hardware/sensor.py` |
| `mejorada.py` | `src/ui/app_responsive.py` |
| `imagenes/` | `assets/images/` |

---

## Dependencias

| Paquete | Uso |
|---------|-----|
| customtkinter | Interfaz gráfica moderna |
| Pillow | Procesamiento de imágenes |
| numpy | Cálculos numéricos |
| matplotlib | Gráficos polares del radar |
| roboticstoolbox-python | Modelo cinemático 3D |
| pyserial | Comunicación serial |
| cartopy | Mapas geográficos |
| pandas | Procesamiento de datos CSV |
| tkintermapview | Mapa interactivo |

---

## Uso del Ejecutable

El ejecutable compilado no requiere Python. Doble clic en `SoftwareRadar.exe` para iniciar.

**Requisitos del sistema**: Windows 10/11 64-bit, 4 GB RAM mínimo (8 GB recomendado), 500 MB de disco.

**Estructura de datos junto al ejecutable:**

```
SoftwareRadar.exe
└── output/
    └── Lecturas RADAR/
        └── tu_archivo.csv
```

Para compilar el ejecutable, ver `docs/COMO_COMPILAR.md`.

---

## Solución de Problemas

**"No module named 'src'"**: Ejecutar desde la raíz del proyecto con `python run.py`.

**"No module named XXX"**: Reinstalar dependencias con `pip install -r requirements.txt`.

**Error numpy.core.multiarray**: `pip uninstall numpy -y && pip install "numpy<2"`.

**No aparecen puertos COM**: Verificar conexión USB, instalar drivers (CH340, CP2102 o FTDI), abrir Administrador de dispositivos para confirmar el puerto.

**Puerto ya en uso**: Cerrar otros programas que usen el puerto (Arduino IDE, Putty, etc.).

**Antivirus bloquea el ejecutable**: Agregar excepción. Es un falso positivo común con PyInstaller.

**Windows SmartScreen**: Click en "Más información" y luego "Ejecutar de todas formas".
