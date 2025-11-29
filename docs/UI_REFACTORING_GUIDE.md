# 🎨 Guía de Refactorización de UI - Software Radar

Esta guía explica cómo refactorizar la interfaz gráfica (`mejorada.py`) en componentes modulares.

---

## 📋 Estado Actual

El archivo `mejorada.py` (1192 líneas) contiene:
- ✅ Clase `App`: Ventana principal
- ✅ Clase `panel_control`: Panel de control de motores
- ✅ Clase `panel_visualizacion`: Panel de visualización del radar
- ✅ Clases auxiliares: `barrido`, `radio`, `grafico`

**Problema**: Todo en un solo archivo dificulta el mantenimiento.

---

## 🎯 Objetivo

Dividir en componentes modulares:

```
src/ui/
├── app.py                      # Aplicación principal (App)
├── panels/
│   ├── control_panel.py        # Panel de control
│   └── visualization_panel.py  # Panel de visualización
├── widgets/
│   ├── graphics.py             # Gráficos del radar (grafico, barrido, radio)
│   └── motor_control.py        # Widgets de control de motores
└── components/
    ├── serial_config.py        # Configuración serial
    └── robot_display.py        # Display 3D del robot
```

---

## 🔧 Plan de Refactorización

### Fase 1: Crear Estructura Base

```python
# src/ui/__init__.py
"""Módulos de interfaz gráfica."""
from .app import RadarApp

__all__ = ["RadarApp"]
```

### Fase 2: Extraer Clases de Datos

**Archivo**: `src/ui/widgets/graphics.py`

```python
"""Widgets y clases para gráficos del radar."""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class Radio:
    """Representa un radio de medición del radar."""
    
    def __init__(self, radio_arreglo: List):
        """
        Inicializa un radio.
        
        Args:
            radio_arreglo: Array con datos del radio.
        """
        self.aceptacion = radio_arreglo[1]
        self.anuncio_modo = radio_arreglo[2]
        self.fallos = radio_arreglo[3]
        self.operacion = radio_arreglo[4]
        self.inclinacion = radio_arreglo[5]
        self.ganancia = radio_arreglo[6]
        self.rango = radio_arreglo[7]
        self.datos = radio_arreglo[9]


class Barrido:
    """Representa un barrido completo del radar."""
    
    def __init__(self, arreglo_interpretado: List):
        """
        Inicializa un barrido.
        
        Args:
            arreglo_interpretado: Datos interpretados del radar.
        """
        self.radios: Dict[int, Radio] = {}
        
        for actual in arreglo_interpretado:
            radio_id = int(actual[8])
            if radio_id not in self.radios:
                self.radios[radio_id] = Radio(actual)
        
        # Procesar fallos
        self.fallos = list(set(
            item 
            for actual in self.radios 
            for item in self.radios[actual].fallos 
            if len(self.radios[actual].fallos) > 0
        ))
        
        # Procesar anuncios
        self.anuncio = list(set(
            item 
            for actual in self.radios 
            for item in self.radios[actual].anuncio_modo 
            if len(self.radios[actual].anuncio_modo) > 0
        ))
        
        # Extraer parámetros del primer radio
        if self.radios:
            primera_clave = next(iter(self.radios))
            self.ganancia = self.radios[primera_clave].ganancia
            self.inclinacion = self.radios[primera_clave].inclinacion
            self.operacion = self.radios[primera_clave].operacion
            self.aceptacion = 1 if self.radios[primera_clave].aceptacion == 2 else 0
        
        # Calcular rango máximo
        self.rango = max(
            (self.radios[actual].rango for actual in self.radios),
            default=0
        )
        
        # Determinar tipo de barrido
        if arreglo_interpretado and arreglo_interpretado[0][0] == "00101101":
            self.tipo_vp = 1
        elif arreglo_interpretado and arreglo_interpretado[0][0] == "01111001":
            self.tipo_vp = 2
            self.anuncio = [7]
        else:
            self.tipo_vp = 1


class RadarGraphic:
    """Gestiona los gráficos polares del radar."""
    
    COLOR_MAP = {
        0: (0, 0, 0, 0),  # Transparente
        1: "green",       # Ecos débiles
        2: "yellow",      # Ecos moderados
        3: "red",         # Ecos fuertes
        4: "magenta"      # Ecos muy intensos
    }
    
    def __init__(self, num_pixels: int = 512):
        """
        Inicializa el gráfico del radar.
        
        Args:
            num_pixels: Número de píxeles por radio.
        """
        self.num_pixels = num_pixels
        self._setup_plot()
    
    def _setup_plot(self):
        """Configura el plot inicial."""
        self.fig, self.ax = plt.subplots(
            subplot_kw={'polar': True},
            figsize=(8.6, 7.6)
        )
        
        self.lines = {}
        for angulo in range(-49, 50):
            self.lines[angulo] = [
                self.ax.plot(
                    [0, 0], [0, 0],
                    color=(0, 0, 0, 0),
                    lw=3,
                    zorder=1
                )[0] for _ in range(self.num_pixels - 1)
            ]
        
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_thetamin(-49)
        self.ax.set_thetamax(49)
        self.ax.grid(zorder=3)
        self.ax.set_title("Datos del radar", va='bottom')
        
        self.configurar_grids_radiales()
    
    def configurar_grids_radiales(
        self,
        rango: int = None,
        es_perfil_vertical: bool = False
    ):
        """
        Configura los grids radiales.
        
        Args:
            rango: Rango máximo del radar.
            es_perfil_vertical: Si es modo perfil vertical.
        """
        rango = rango or 100
        
        if es_perfil_vertical:
            step = max(10, rango // 4)
        else:
            step = max(5, rango // 4)
        
        self.ax.set_rgrids(radii=np.arange(0, rango + step, step))
    
    def actualizar_grafico(
        self,
        barrido: Barrido,
        lat: float,
        lon: float,
        compass: float
    ):
        """
        Actualiza el gráfico con nuevo barrido.
        
        Args:
            barrido: Datos del barrido.
            lat: Latitud actual.
            lon: Longitud actual.
            compass: Orientación de la brújula.
        """
        if barrido.tipo_vp == 1:
            self._actualizar_vista_normal(barrido)
        elif barrido.tipo_vp == 2:
            self._actualizar_perfil_vertical(barrido)
    
    def _actualizar_vista_normal(self, barrido: Barrido):
        """Actualiza vista normal del radar."""
        for angulo, radio in barrido.radios.items():
            valores = np.linspace(0, radio.rango, self.num_pixels)
            angulo_rad = np.deg2rad(angulo)
            
            if angulo in self.lines:
                for i in range(len(radio.datos) - 1):
                    self.lines[angulo][i].set_data(
                        [angulo_rad, angulo_rad],
                        [valores[i], valores[i + 1]]
                    )
                    self.lines[angulo][i].set_color(
                        self.COLOR_MAP[radio.datos[i]]
                    )
        
        self.ax.set_ylim(0, barrido.rango)
        self.configurar_grids_radiales(barrido.rango, False)
    
    def _actualizar_perfil_vertical(self, barrido: Barrido):
        """Actualiza perfil vertical del radar."""
        for angulo, radio in barrido.radios.items():
            valores = np.linspace(0, radio.rango, self.num_pixels)
            angulo_rad = -np.deg2rad(angulo)
            
            if angulo in self.lines:
                for i in range(len(radio.datos) - 1):
                    self.lines[angulo][i].set_data(
                        [angulo_rad, angulo_rad],
                        [valores[i], valores[i + 1]]
                    )
                    self.lines[angulo][i].set_color(
                        self.COLOR_MAP[radio.datos[i]]
                    )
        
        self.ax.set_ylim(0, barrido.rango)
        self.ax.set_theta_zero_location("E")
        angles_vp = np.arange(-30, 31, 10)
        self.ax.set_thetagrids(
            angles=angles_vp,
            labels=[f"{-x}°" if x != 0 else "0°" for x in angles_vp]
        )
        self.ax.set_title("Perfil vertical", va='bottom')
        self.configurar_grids_radiales(barrido.rango, True)


# Aliases legacy
grafico = RadarGraphic
barrido = Barrido
radio = Radio
```

### Fase 3: Extraer Panel de Control

**Archivo**: `src/ui/panels/control_panel.py`

```python
"""Panel de control del radar."""
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging

logger = logging.getLogger(__name__)


class ControlPanel(ctk.CTkFrame):
    """Panel de control de motores y configuración del radar."""
    
    def __init__(self, parent, serial_comm, **kwargs):
        """
        Inicializa el panel de control.
        
        Args:
            parent: Widget padre.
            serial_comm: Instancia de SerialCommunication.
        """
        super().__init__(parent, **kwargs)
        
        self.serial_comm = serial_comm
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        # Crear widgets...
        pass
    
    # Resto de métodos del panel...
```

### Fase 4: Extraer Panel de Visualización

**Archivo**: `src/ui/panels/visualization_panel.py`

```python
"""Panel de visualización del radar."""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import logging

logger = logging.getLogger(__name__)


class VisualizationPanel(ctk.CTkFrame):
    """Panel de visualización de datos del radar."""
    
    def __init__(self, parent, serial_comm, **kwargs):
        """
        Inicializa el panel de visualización.
        
        Args:
            parent: Widget padre.
            serial_comm: Instancia de SerialCommunication.
        """
        super().__init__(parent, **kwargs)
        
        self.serial_comm = serial_comm
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        # Crear widgets...
        pass
    
    # Resto de métodos del panel...
```

### Fase 5: Aplicación Principal

**Archivo**: `src/ui/app.py`

```python
"""Aplicación principal del Software Radar."""
import customtkinter as ctk
from PIL import Image
import logging

from src.config import Settings
from src.core.communication import SerialCommunication
from src.ui.panels.control_panel import ControlPanel
from src.ui.panels.visualization_panel import VisualizationPanel

logger = logging.getLogger(__name__)


class RadarApp:
    """Aplicación principal del Software Radar."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.settings = Settings()
        self._setup_window()
        self._setup_communication()
        self._setup_ui()
    
    def _setup_window(self):
        """Configura la ventana principal."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(self.settings.window_title)
        
        # Centrar ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - self.settings.window_width) // 2
        y = (screen_height - self.settings.window_height) // 2
        
        self.root.geometry(
            f"{self.settings.window_width}x{self.settings.window_height}"
            f"+{x}+{y}"
        )
    
    def _setup_communication(self):
        """Configura la comunicación serial."""
        self.serial = SerialCommunication()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Menú lateral
        self.menu = ctk.CTkFrame(
            self.root,
            fg_color="#1F6AA5",
            width=220
        )
        self.menu.pack(side=ctk.LEFT, fill='both', expand=False)
        
        # Contenedor principal
        self.container = ctk.CTkFrame(
            self.root,
            fg_color="#242424"
        )
        self.container.pack(side=ctk.RIGHT, fill='both', expand=True)
        
        # Título
        title = ctk.CTkLabel(
            self.menu,
            text="\nR A D A R\n",
            font=("Arial Black", 20),
            padx=30
        )
        title.pack(side=ctk.TOP)
        
        # Botones de navegación
        self._create_navigation_buttons()
        
        # Logo inicial
        self._show_welcome_screen()
    
    def _create_navigation_buttons(self):
        """Crea los botones de navegación."""
        # Cargar iconos
        icon_control = self._load_icon("Icono palanca.png")
        icon_radar = self._load_icon("Icono radar.png")
        
        # Botón Control
        btn_control = ctk.CTkButton(
            self.menu,
            text="Control",
            image=icon_control,
            width=220,
            command=self.show_control_panel
        )
        btn_control.pack(side=ctk.TOP)
        
        # Botón Visualización
        btn_viz = ctk.CTkButton(
            self.menu,
            text="Visualización",
            image=icon_radar,
            width=220,
            command=self.show_visualization_panel
        )
        btn_viz.pack(side=ctk.TOP)
    
    def _load_icon(self, filename):
        """Carga un icono."""
        from pathlib import Path
        icon_path = self.settings.IMAGES_DIR / filename
        return ctk.CTkImage(
            light_image=Image.open(icon_path),
            dark_image=Image.open(icon_path),
            size=(50, 50)
        )
    
    def _show_welcome_screen(self):
        """Muestra la pantalla de bienvenida."""
        # Implementar...
        pass
    
    def show_control_panel(self):
        """Muestra el panel de control."""
        if not hasattr(self, 'control_panel'):
            self.control_panel = ControlPanel(
                self.container,
                self.serial
            )
        self.control_panel.tkraise()
    
    def show_visualization_panel(self):
        """Muestra el panel de visualización."""
        if not self.serial.status:
            messagebox.showerror(
                "Sin comunicación serial",
                "Establezca primero la comunicación serial"
            )
            return
        
        if not hasattr(self, 'viz_panel'):
            self.viz_panel = VisualizationPanel(
                self.container,
                self.serial
            )
        self.viz_panel.tkraise()
    
    def run(self):
        """Ejecuta la aplicación."""
        logger.info("Iniciando interfaz gráfica")
        self.root.mainloop()
    
    def cleanup(self):
        """Limpia recursos antes de cerrar."""
        if hasattr(self, 'serial') and self.serial.status:
            self.serial.disconnect()
        logger.info("Aplicación cerrada correctamente")
```

---

## ✅ Checklist de Refactorización

- [x] Crear estructura de carpetas `src/ui/`
- [ ] Extraer clases de datos (`Radio`, `Barrido`, `RadarGraphic`)
- [ ] Extraer `ControlPanel` de `panel_control`
- [ ] Extraer `VisualizationPanel` de `panel_visualizacion`
- [ ] Crear `RadarApp` principal
- [ ] Actualizar imports en `mejorada.py`
- [ ] Probar la aplicación refactorizada
- [ ] Eliminar `mejorada.py` legacy (una vez confirmado que funciona)

---

## 🧪 Cómo Probar

```python
# tests/test_ui/test_graphics.py
import pytest
from src.ui.widgets.graphics import Radio, Barrido, RadarGraphic

def test_radio_creation():
    data = [None, 2, [], [], 1, 0, -10, 100, 45, [1,2,3,4]]
    radio = Radio(data)
    assert radio.aceptacion == 2
    assert radio.operacion == 1

def test_barrido_creation():
    # Crear datos de prueba
    pass

def test_radar_graphic():
    graphic = RadarGraphic(num_pixels=512)
    assert graphic.num_pixels == 512
    assert len(graphic.lines) > 0
```

---

## 📚 Recursos

- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [Matplotlib Docs](https://matplotlib.org/)
- [Clean Architecture in Python](https://blog.cleancoder.com)

---

## 💡 Consejos

1. **Refactoriza incrementalmente**: Un componente a la vez
2. **Prueba constantemente**: Después de cada cambio
3. **Mantén el código legacy**: Hasta confirmar que el nuevo funciona
4. **Documenta**: Añade docstrings a todas las clases y métodos
5. **Type hints**: Usa anotaciones de tipo

---

**Estado**: 🚧 Guía completada, refactorización pendiente de implementación

*Para implementar, sigue los pasos en orden y prueba después de cada fase.*

