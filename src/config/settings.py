"""
Configuración global del sistema de radar.
"""
import os
import sys
from pathlib import Path


def get_base_path():
    """
    Obtiene la ruta base de la aplicación.
    
    - En desarrollo: retorna el directorio raíz del proyecto
    - En ejecutable: retorna el directorio donde está el .exe
    """
    if getattr(sys, 'frozen', False):
        # Ejecutando como ejecutable empaquetado (PyInstaller)
        # sys.executable apunta al .exe
        return Path(sys.executable).parent
    else:
        # Ejecutando como script de Python
        return Path(__file__).parent.parent.parent


def get_internal_assets_path():
    """
    Obtiene la ruta de assets internos (empaquetados en el ejecutable).
    
    - En desarrollo: usa la carpeta assets/ del proyecto
    - En ejecutable: usa _MEIPASS (carpeta temporal de PyInstaller)
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller extrae recursos a una carpeta temporal
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent


# Directorios del proyecto
PROJECT_ROOT = get_base_path()
INTERNAL_ROOT = get_internal_assets_path()

# SRC_DIR solo existe en desarrollo
SRC_DIR = Path(__file__).parent.parent if not getattr(sys, 'frozen', False) else INTERNAL_ROOT / "src"

# Assets internos (imágenes, iconos) - empaquetados con el ejecutable
ASSETS_DIR = INTERNAL_ROOT / "assets"

# Datos externos (output, sensores) - junto al ejecutable
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output"
SENSORS_DIR = DATA_DIR / "sensors"

# Carpeta legacy de lecturas de radar (para compatibilidad)
RADAR_OUTPUT_DIR = PROJECT_ROOT / "output" / "Lecturas RADAR"

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
MOTOR_INCLINATION_MIN = 0
MOTOR_INCLINATION_MAX = 34

# Configuración del sensor meteorológico
SENSOR_DATA_FILE = "CR310_RK900_10.csv"

# Rutas de imágenes
IMAGES_DIR = ASSETS_DIR / "images"
ICON_RADAR = IMAGES_DIR / "Icono radar.png"
ICON_CONTROL = IMAGES_DIR / "Icono palanca.png"
ICON_FAC = IMAGES_DIR / "Icono fac.png"


def ensure_data_directories():
    """
    Crea los directorios de datos si no existen.
    Útil para el primer uso del ejecutable.
    """
    directories = [DATA_DIR, OUTPUT_DIR, SENSORS_DIR, RADAR_OUTPUT_DIR]
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)


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
        self.radar_output_dir = RADAR_OUTPUT_DIR
        
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.window_title = WINDOW_TITLE
        
        self.baudrates = BAUDRATES
        self.default_baudrate = DEFAULT_BAUDRATE
        self.serial_timeout = SERIAL_TIMEOUT
        
        self.radar_color_map = RADAR_COLOR_MAP
        self.radar_num_pixels = RADAR_NUM_PIXELS
        
        # Asegurar que existan los directorios de datos
        ensure_data_directories()
        
        self._initialized = True
    
    def get_radar_file_path(self, filename):
        """
        Obtiene la ruta completa para un archivo de lecturas de radar.
        
        Args:
            filename: Nombre del archivo (ej: '31_03_2025_2.csv')
        
        Returns:
            Path completo al archivo
        """
        return self.radar_output_dir / filename
    
    @staticmethod
    def is_frozen():
        """Retorna True si la aplicación está corriendo como ejecutable."""
        return getattr(sys, 'frozen', False)

