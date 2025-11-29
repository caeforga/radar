"""
Software Radar - Punto de entrada principal.

Este es el archivo principal para ejecutar la aplicación.
"""
import sys
import logging
from pathlib import Path

# Añadir el directorio raíz al path de Python
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Importar después de añadir al path
from src.ui.app import RadarApp
from src.config.settings import Settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('radar.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Función principal de la aplicación."""
    try:
        logger.info("=" * 60)
        logger.info("Iniciando Software Radar")
        logger.info("=" * 60)
        
        # Cargar configuración
        settings = Settings()
        logger.info(f"Directorio del proyecto: {settings.project_root}")
        
        # Iniciar aplicación
        app = RadarApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Aplicación finalizada")


if __name__ == "__main__":
    main()

