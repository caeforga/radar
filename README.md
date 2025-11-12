# 📡 Software Radar

Sistema de control y visualización para radar meteorológico con interfaz gráfica moderna desarrollada en Python.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Descripción

Software Radar es una aplicación de escritorio diseñada para controlar y visualizar datos de un sistema de radar meteorológico en tiempo real. Incluye control de motores, adquisición de datos GPS, integración con sensores meteorológicos y visualización polar de los datos capturados.

### ✨ Características Principales

- 🎮 **Control de Motores**: Control preciso de rotación e inclinación del radar
- 📊 **Visualización en Tiempo Real**: Gráficos polares actualizados en tiempo real
- 🌍 **Integración GPS**: Captura de coordenadas y orientación
- 🌤️ **Datos Meteorológicos**: Monitoreo de temperatura, viento y precipitaciones
- 🔧 **Configuración Avanzada**: Ajuste de ganancia, rango y modos de operación
- 🤖 **Simulación 3D**: Visualización del modelo cinemático del robot
- 💾 **Registro de Datos**: Almacenamiento automático de lecturas

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.12** o superior
- **Microsoft Visual C++ Build Tools** (necesario para roboticstoolbox)
- **Hardware**: Puerto serial para conexión con el radar

### Paso 1: Instalar Microsoft C++ Build Tools

1. Descarga desde: [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Durante la instalación, selecciona:
   - ✅ **"Desarrollo para el escritorio con C++"**
3. Completa la instalación (puede tardar 10-15 minutos)
4. **Reinicia tu terminal** después de la instalación

### Paso 2: Clonar el Repositorio

```bash
cd C:\Users\TuUsuario\Documents
git clone https://github.com/tuusuario/SoftwareRadar.git
cd SoftwareRadar
```

### Paso 3: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1

# En Windows CMD:
venv\Scripts\activate.bat

# En Linux/Mac:
source venv/bin/activate
```

### Paso 4: Instalar Dependencias

```bash
# Actualizar pip (recomendado)
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

**⚠️ Nota importante sobre NumPy:**  
El proyecto requiere `numpy<2` debido a incompatibilidades de `roboticstoolbox-python` con NumPy 2.x. Esto ya está especificado en `requirements.txt`.

---

## ▶️ Ejecución

### Ejecutar la Aplicación

```bash
python mejorada.py
```

La interfaz gráfica se abrirá mostrando la pantalla principal con el logo de la facultad y dos botones principales:

- **Control**: Panel de control de motores y conexión serial
- **Visualización**: Panel de visualización del radar

---

## 📖 Guía de Uso

### 1️⃣ Panel de Control

#### Conexión Serial
1. Haz clic en **"Control"**
2. Selecciona el **Puerto COM** correspondiente
3. Selecciona la velocidad (**Baud Rate**, típicamente 9600)
4. Haz clic en **"Conectar"**

#### Modos de Operación
- **OFF**: Radar apagado
- **Standby**: Modo espera (bajo consumo)
- **TEST**: Modo de prueba con controles habilitados
- **ON**: Modo operación completa

#### Control de Motores
- **Motor de Rotación**: Slider horizontal (-180° a +180°)
- **Motor de Inclinación**: Slider vertical (-60° a +60°)
- Los valores se envían al hardware al soltar el slider

#### Configuración del Radar
- **Ganancia**: Ajuste de sensibilidad (-31.5 dB a 0 dB)
- **Inclinación**: Ajuste fino de ángulo (-15° a +15°)
- **Rango**: Botones ▲/▼ para cambiar rango de detección
- **Track (TRK)**: Ajuste del ángulo de seguimiento (◄/►)
- **Perfil Vertical (VP)**: Activar/desactivar modo de escaneo vertical

### 2️⃣ Panel de Visualización

Para acceder a la visualización:
1. Asegúrate de estar **conectado** al puerto serial
2. Haz clic en **"Visualización"**

#### Información Mostrada
- **Gráfico Polar**: Datos del radar en coordenadas polares
- **Estado de Operación**: Indicadores de modo actual
- **Fallos**: Notificaciones de errores del sistema
- **Coordenadas GPS**: Latitud y longitud actuales
- **Orientación**: Dirección de la brújula
- **Datos Meteorológicos**: 
  - Fecha y hora de última lectura
  - Temperatura
  - Dirección del viento
  - Nivel de precipitaciones

#### Interpretación de Colores
- 🟢 **Verde**: Ecos débiles
- 🟡 **Amarillo**: Ecos moderados
- 🔴 **Rojo**: Ecos fuertes
- 🟣 **Magenta**: Ecos muy intensos

---

## 📁 Estructura del Proyecto

```
SoftwareRadar/
├── mejorada.py                 # Aplicación principal
├── ComSerial.py                # Manejo de comunicación serial
├── Interpretacion.py           # Procesamiento de datos del radar
├── GPS.py                      # Procesamiento de datos GPS
├── CargaSensor.py              # Lectura de sensor meteorológico
├── Captura.py                  # Captura de datos con Logic Analyzer
├── ControlMotores.py           # Control de motores
├── GraficoObject.py            # Generación de gráficos
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Este archivo
│
├── CTkXYFrame/                 # Componente customizado de tkinter
│   ├── __init__.py
│   └── ctk_xyframe.py
│
├── imagenes/                   # Recursos gráficos
│   ├── Icono radar.png
│   ├── Icono palanca.png
│   └── Icono fac.png
│
├── output/                     # Datos capturados
│   ├── Lecturas RADAR/        # Archivos CSV con lecturas
│   └── RawData/                # Datos crudos (.sal)
│
├── FirmwareESP32/              # Firmware para ESP32
│   └── FirmwareESP32.ino
│
└── PCB FINAL/                  # Diseño de PCB (KiCad)
    ├── baquelita.kicad_pcb
    ├── baquelita.kicad_sch
    └── Gerbers/
```

---

## 🔧 Solución de Problemas

### ❌ Error: `ModuleNotFoundError: No module named 'roboticstoolbox'`

**Solución:**
```bash
pip install roboticstoolbox-python
```

### ❌ Error: `numpy.core.multiarray failed to import`

**Causa:** Incompatibilidad entre NumPy 2.x y roboticstoolbox

**Solución:**
```bash
pip uninstall numpy -y
pip install "numpy<2"
```

### ❌ Error: `Microsoft Visual C++ 14.0 or greater is required`

**Solución:**
1. Instala [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Selecciona "Desarrollo para el escritorio con C++"
3. Reinicia la terminal después de la instalación

### ❌ Error: "Sin comunicación serial"

**Solución:**
1. Verifica que el dispositivo esté conectado
2. Comprueba el puerto COM en el Administrador de Dispositivos
3. Asegúrate de tener los drivers correctos instalados
4. Prueba con diferentes velocidades de baudios

### ❌ La aplicación se cierra inmediatamente

**Solución:**
```bash
# Ejecuta desde la terminal para ver mensajes de error
python mejorada.py
```

### ⚠️ Archivo `CR310_RK900_10.csv` no encontrado

**Solución:**
- Asegúrate de que el archivo del sensor meteorológico esté en la carpeta raíz
- Si no tienes el sensor, puedes crear un archivo CSV vacío con las columnas:
  ```csv
  TIMESTAMP,Temperature,Wind_Direction,Precipitation
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

---

## 🛠️ Hardware Requerido

- **Radar**: Sistema de radar compatible con protocolo Manchester
- **Motores**: Sistema de 2 grados de libertad (rotación + inclinación)
- **GPS**: Módulo GPS compatible (NMEA)
- **Brújula**: Sensor de orientación
- **Sensor Meteorológico**: Estación meteorológica Campbell Scientific CR310
- **Interfaz**: ESP32 o Arduino para comunicación serial

---

## 📊 Formato de Datos

### Datos de Entrada (Serial)
El sistema espera datos codificados en Manchester con:
- **Tasa de bits**: 1 Mbps
- **Formato**: Tramas de 512 bytes
- **Protocolo**: Custom (ver `Interpretacion.py`)

### Datos GPS
- **Formato**: NMEA (GGA, RMC)
- **Baud Rate**: Configurable

### Sensor Meteorológico
- **Formato**: CSV
- **Columnas**: TIMESTAMP, Temperature, Wind_Direction, Precipitation

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 Autores

- **Equipo de Desarrollo** - Universidad/Facultad

---

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Abre un [Issue](https://github.com/tuusuario/SoftwareRadar/issues) en GitHub
3. Contacta al equipo de desarrollo

---

## 🔄 Changelog

### Versión 1.1.1 (Actual)
- ✅ Soporte para NumPy 1.x
- ✅ Interfaz mejorada con CustomTkinter
- ✅ Visualización de mapas con Cartopy
- ✅ Integración con sensor meteorológico
- ✅ Modo de perfil vertical

---

## ⭐ Agradecimientos

- Robotics Toolbox for Python
- CustomTkinter por la interfaz moderna
- Cartopy por los mapas geográficos
- La comunidad de Python

---

**¡Gracias por usar Software Radar!** 📡✨

