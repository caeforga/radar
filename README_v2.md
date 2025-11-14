# 📡 Software Radar v2.0

> Sistema de control y visualización para radar meteorológico con arquitectura limpia y modular.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Clean-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎉 ¿Qué hay de nuevo en v2.0?

- ✨ **Arquitectura Limpia**: Código completamente reestructurado siguiendo principios SOLID
- 📦 **Modularidad**: Componentes independientes y fáciles de mantener
- 🧪 **Testeable**: Estructura preparada para tests unitarios
- 📚 **Documentación Completa**: Docstrings, type hints y guías detalladas
- 🔧 **Configuración Centralizada**: Settings en un solo lugar
- 🪵 **Logging Estructurado**: Sistema de logs profesional
- 🔄 **Retrocompatibilidad**: Funciones legacy para código existente

---

## 📋 Descripción

Software Radar es una aplicación de escritorio diseñada para controlar y visualizar datos de un sistema de radar meteorológico en tiempo real. Versión 2.0 presenta una arquitectura completamente rediseñada para mejor mantenibilidad y escalabilidad.

### ✨ Características

- 🎮 **Control de Motores**: Control preciso de rotación e inclinación
- 📊 **Visualización en Tiempo Real**: Gráficos polares actualizados
- 🌍 **Integración GPS**: Captura de coordenadas y orientación
- 🌤️ **Datos Meteorológicos**: Monitoreo de temperatura, viento y precipitaciones
- 🔧 **Configuración Avanzada**: Ajuste de ganancia, rango y modos
- 🤖 **Simulación 3D**: Visualización del modelo cinemático del robot
- 💾 **Registro de Datos**: Almacenamiento automático de lecturas

---

## 📁 Estructura del Proyecto

```
SoftwareRadar/
├── src/                          # Código fuente
│   ├── config/                   # Configuración
│   ├── core/                     # Lógica de negocio
│   │   ├── communication/        # Comunicación serial
│   │   ├── hardware/             # GPS, sensores, motores
│   │   └── data/                 # Procesamiento de datos
│   ├── ui/                       # Interfaz gráfica
│   │   ├── components/           # Componentes reutilizables
│   │   ├── panels/               # Paneles principales
│   │   └── widgets/              # Widgets especializados
│   ├── utils/                    # Utilidades
│   └── main.py                   # Punto de entrada
├── assets/                       # Recursos estáticos
├── data/                         # Datos del sistema
├── firmware/                     # Firmware de dispositivos
├── hardware/                     # Diseños PCB
├── tests/                        # Tests unitarios
├── docs/                         # Documentación
├── run.py                        # Script de ejecución
└── requirements.txt              # Dependencias
```

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para detalles completos.

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.12** o superior
- **Microsoft Visual C++ Build Tools**
- **Hardware**: Puerto serial para conexión

### Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/tuusuario/SoftwareRadar.git
cd SoftwareRadar

# 2. Crear entorno virtual
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
python run.py
```

Ver [instalación detallada en README.md original](README.md#-instalación)

---

## ▶️ Uso

### Ejecutar la Aplicación

```bash
# Método 1: Script de ejecución (recomendado)
python run.py

# Método 2: Como módulo
python -m src.main

# Método 3: Directamente
python src/main.py
```

### Uso Programático

```python
from src.core.communication import SerialCommunication
from src.core.hardware import GPSParser, WeatherSensor
from src.config import Settings

# Configuración
settings = Settings()

# Comunicación serial
with SerialCommunication() as comm:
    comm.arduino.port = "COM3"
    comm.arduino.baudrate = 9600
    if comm.connect():
        comm.send_data("comando")
        data = comm.read_data()

# GPS
gps_data = GPSParser.parse_nmea("$GNGGA,...")

# Sensor meteorológico
sensor = WeatherSensor("data/sensors/CR310_RK900_10.csv")
reading = sensor.get_last_reading()
temp = sensor.get_temperature()
```

---

## 📖 Documentación

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Arquitectura detallada del proyecto
- **[MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)**: Guía de migración desde v1.x
- **[GIT_GUIDE.md](GIT_GUIDE.md)**: Guía de uso de Git
- **[README.md (original)](README.md)**: Documentación completa v1.x

### Documentación de API

```python
# Ver docstrings en el código
help(SerialCommunication)
help(GPSParser)
help(WeatherSensor)
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src tests/

# Tests específicos
pytest tests/test_hardware/test_gps.py -v
```

---

## 🔧 Configuración

### Settings Centralizados

```python
from src.config import Settings

settings = Settings()

# Rutas
print(settings.project_root)
print(settings.assets_dir)

# Configuración UI
print(settings.window_width)
print(settings.window_height)

# Configuración serial
print(settings.baudrates)
print(settings.default_baudrate)
```

### Variables de Entorno (opcional)

Crea un archivo `.env` en la raíz:

```env
RADAR_PORT=COM3
RADAR_BAUDRATE=9600
LOG_LEVEL=INFO
```

---

## 🔄 Migración desde v1.x

Si estás actualizando desde la versión anterior:

1. Lee la **[Guía de Migración](docs/MIGRATION_GUIDE.md)**
2. Actualiza tus imports
3. Prueba la aplicación

### Compatibilidad hacia atrás

Los módulos refactorizados mantienen aliases para compatibilidad:

```python
# Todavía funciona (legacy)
from src.core.communication.serial_comm import comunicacion
serial = comunicacion()

# Pero se recomienda usar
from src.core.communication import SerialCommunication
serial = SerialCommunication()
```

---

## 📦 Dependencias

| Paquete | Versión | Descripción |
|---------|---------|-------------|
| customtkinter | 5.2.2 | Interfaz gráfica moderna |
| Pillow | 10.1.0 | Procesamiento de imágenes |
| numpy | <2.0 | Cálculos numéricos |
| matplotlib | 3.8.2 | Generación de gráficos |
| roboticstoolbox-python | 1.1.1 | Cinemática del robot |
| pyserial | 3.5 | Comunicación serial |
| cartopy | 0.25.0 | Mapas geográficos |
| pandas | latest | Procesamiento de datos |

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Sigue la estructura de carpetas establecida
4. Añade tests para nuevo código
5. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
6. Push a la rama (`git push origin feature/AmazingFeature`)
7. Abre un Pull Request

### Guías de Estilo

- **Python**: PEP 8
- **Docstrings**: Google style
- **Type Hints**: Requerido para nuevas funciones
- **Logging**: Usar `logging` en lugar de `print`

---

## 🐛 Solución de Problemas

### Error: "No module named 'src'"

```bash
# Ejecuta desde la raíz del proyecto
cd SoftwareRadar
python run.py
```

### Error: numpy.core.multiarray

```bash
pip uninstall numpy -y
pip install "numpy<2"
```

### Error: Microsoft Visual C++ required

Instala [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Ver más en [README.md original](README.md#-solución-de-problemas)

---

## 📊 Comparación de Versiones

| Aspecto | v1.x | v2.0 |
|---------|------|------|
| **Estructura** | Archivos en raíz | Arquitectura modular |
| **Testing** | ❌ No estructurado | ✅ Preparado para tests |
| **Documentación** | README básico | Docs completa + docstrings |
| **Configuración** | Hardcoded | Settings centralizados |
| **Logging** | print statements | logging estructurado |
| **Type Hints** | ❌ No | ✅ Completo |
| **Mantenibilidad** | Media | Alta |

---

## 🗺️ Roadmap

- [ ] **v2.1**: Tests unitarios completos
- [ ] **v2.2**: API REST para integración externa
- [ ] **v2.3**: Dashboard web
- [ ] **v2.4**: Soporte para múltiples radares
- [ ] **v3.0**: Reescritura en Qt6

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👥 Autores

- **Equipo de Desarrollo** - Software Radar v2.0

---

## 🙏 Agradecimientos

- Robotics Toolbox for Python
- CustomTkinter
- Cartopy
- La comunidad de Python

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tuusuario/SoftwareRadar/issues)
- **Documentación**: Ver carpeta `docs/`
- **Email**: support@ejemplo.com

---

**Software Radar v2.0** - Construido con ❤️ y ☕

*Para documentación de v1.x, ver [README.md](README.md)*

