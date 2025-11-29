"""
Configuración global del sistema de radar.
"""
import os
from pathlib import Path

# Directorios del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output"
SENSORS_DIR = DATA_DIR / "sensors"

# Configuración de la interfaz
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Software Radar"

# Configuración de comunicación serial
DEFAULT_BAUDRATE = 9600
BAUDRATES = ['1200', '2400', '4800', '9600', '19200', '38400', '115200']
SERIAL_TIMEOUT = 0.5

# Configuración del radar
RADAR_UPDATE_INTERVAL = 10000  # ms
RADAR_NUM_PIXELS = 512

# Configuración de colores para el radar
RADAR_COLOR_MAP = {
    0: (0, 0, 0, 0),      # Transparente
    1: "green",           # Ecos débiles
    2: "yellow",          # Ecos moderados  
    3: "red",             # Ecos fuertes
    4: "magenta"          # Ecos muy intensos
}

# Límites de los motores
MOTOR_ROTATION_MIN = -180
MOTOR_ROTATION_MAX = 180
MOTOR_INCLINATION_MIN = -60
MOTOR_INCLINATION_MAX = 60

# Configuración del sensor meteorológico
SENSOR_DATA_FILE = "CR310_RK900_10.csv"

# Rutas de imágenes
IMAGES_DIR = ASSETS_DIR / "images"
ICON_RADAR = IMAGES_DIR / "Icono radar.png"
ICON_CONTROL = IMAGES_DIR / "Icono palanca.png"
ICON_FAC = IMAGES_DIR / "Icono fac.png"


class Settings:
    """Clase singleton para acceder a la configuración."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.project_root = PROJECT_ROOT
        self.assets_dir = ASSETS_DIR
        self.data_dir = DATA_DIR
        self.output_dir = OUTPUT_DIR
        
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.window_title = WINDOW_TITLE
        
        self.baudrates = BAUDRATES
        self.default_baudrate = DEFAULT_BAUDRATE
        self.serial_timeout = SERIAL_TIMEOUT
        
        self.radar_color_map = RADAR_COLOR_MAP
        self.radar_num_pixels = RADAR_NUM_PIXELS
        
        self._initialized = True

