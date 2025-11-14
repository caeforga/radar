"""
Aplicación principal del Software Radar.

Esta versión usa una interfaz responsiva que se adapta a cualquier pantalla.
"""
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    # Importar la aplicación responsiva
    from src.ui.app_responsive import ResponsiveRadarApp
    
    class RadarApp(ResponsiveRadarApp):
        """
        Aplicación principal del Software Radar con UI responsiva.
        
        Esta versión se adapta automáticamente a cualquier resolución de pantalla.
        """
        pass
    
    logger.info("RadarApp responsiva cargada exitosamente")
    
except ImportError as e:
    logger.error(f"Error al importar app_responsive: {e}")
    logger.info("Intentando cargar versión legacy como fallback")
    
    try:
        # Fallback a versión legacy
        from mejorada import App as LegacyApp
        
        class RadarApp:
            """Wrapper para aplicación legacy (fallback)."""
            
            def __init__(self):
                logger.warning("Usando aplicación legacy (mejorada.py)")
                self._legacy_app = None
            
            def run(self):
                logger.info("Ejecutando aplicación legacy")
                self._legacy_app = LegacyApp()
        
        logger.info("Fallback a legacy exitoso")
        
    except ImportError as e2:
        logger.error(f"Error al cargar fallback: {e2}")
        
        class RadarApp:
            """Placeholder cuando no hay aplicación disponible."""
            
            def __init__(self):
                raise ImportError(
                    "No se pudo cargar ninguna versión de la aplicación.\n"
                    f"Error responsiva: {e}\n"
                    f"Error legacy: {e2}"
                )
            
            def run(self):
                pass

