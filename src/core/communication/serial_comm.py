"""
Módulo de comunicación serial con el hardware del radar.

Este módulo maneja toda la comunicación serial con el dispositivo,
incluyendo la conexión, envío y recepción de datos.
"""
import serial
import serial.tools.list_ports
from threading import Thread, Event
from tkinter import StringVar
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SerialCommunication:
    """
    Gestiona la comunicación serial con el hardware del radar.
    
    Attributes:
        status (bool): Estado de la conexión serial.
        datos_recibidos (StringVar): Variable para almacenar datos recibidos.
        puertos (List[str]): Lista de puertos COM disponibles.
    """
    
    def __init__(self, timeout: float = 0.5):
        """
        Inicializa la comunicación serial.
        
        Args:
            timeout: Tiempo de espera para operaciones serial en segundos.
        """
        self.datos_recibidos = StringVar()
        self.arduino = serial.Serial()
        self.arduino.timeout = timeout
        
        self.baudrates = ['1200', '2400', '4800', '9600', '19200', '38400', '115200']
        self.puertos: List[str] = []
        
        self._signal = Event()
        self._thread: Optional[Thread] = None
        self.status = False
        
        logger.info("SerialCommunication inicializado")
    
    def get_available_ports(self) -> List[str]:
        """
        Obtiene lista de puertos COM disponibles.
        
        Returns:
            Lista de nombres de puertos disponibles.
        """
        self.puertos = [port.device for port in serial.tools.list_ports.comports()]
        logger.debug(f"Puertos disponibles: {self.puertos}")
        return self.puertos
    
    # Mantener compatibilidad con código anterior
    def puertos_disponibles(self):
        """Método legacy. Use get_available_ports() en su lugar."""
        return self.get_available_ports()
    
    def connect(self) -> bool:
        """
        Establece conexión con el puerto serial.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            self.arduino.open()
            if self.arduino.is_open:
                self.arduino.reset_input_buffer()
                self.status = True
                logger.info(f"Conectado a {self.arduino.port}")
                return True
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            self.status = False
        return False
    
    # Método legacy
    def conexion_serial(self):
        """Método legacy. Use connect() en su lugar."""
        return self.connect()
    
    def send_data(self, data: str) -> bool:
        """
        Envía datos a través del puerto serial.
        
        Args:
            data: Cadena de datos a enviar.
            
        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        if self.arduino.is_open:
            try:
                message = str(data) + "\n"
                self.arduino.write(message.encode())
                logger.debug(f"Datos enviados: {data}")
                return True
            except Exception as e:
                logger.error(f"Error al enviar datos: {e}")
                return False
        else:
            logger.warning("No se pueden enviar datos: puerto cerrado")
            return False
    
    # Método legacy
    def enviar_datos(self, data):
        """Método legacy. Use send_data() en su lugar."""
        return self.send_data(data)
    
    def read_data(self) -> Optional[str]:
        """
        Lee datos del puerto serial.
        
        Returns:
            Cadena de datos leída o None si no hay datos.
        """
        try:
            if self.arduino.is_open:
                data = self.arduino.readline().decode("ascii").strip()
                if len(data) >= 1:
                    self.datos_recibidos.set(data)
                    logger.debug(f"Datos recibidos: {data}")
                    return data
        except (TypeError, UnicodeDecodeError) as e:
            logger.error(f"Error al leer datos: {e}")
        return None
    
    # Método legacy
    def leer_datos(self):
        """Método legacy. Use read_data() en su lugar."""
        return self.read_data()
    
    def start_reading_thread(self):
        """Inicia un hilo para lectura continua de datos."""
        if self._thread is None or not self._thread.is_alive():
            self._thread = Thread(target=self.read_data, daemon=True)
            self._signal.set()
            self._thread.start()
            logger.info("Hilo de lectura iniciado")
    
    # Método legacy
    def iniciar_hilo(self):
        """Método legacy. Use start_reading_thread() en su lugar."""
        self.start_reading_thread()
    
    def stop_reading_thread(self):
        """Detiene el hilo de lectura."""
        if self._thread is not None and self._thread.is_alive():
            self._signal.clear()
            self._thread.join(timeout=1.0)
            self._thread = None
            logger.info("Hilo de lectura detenido")
    
    # Método legacy
    def stop_hilo(self):
        """Método legacy. Use stop_reading_thread() en su lugar."""
        self.stop_reading_thread()
    
    def disconnect(self):
        """Cierra la conexión serial."""
        if self.arduino.is_open:
            self.arduino.close()
        self.stop_reading_thread()
        self.status = False
        logger.info("Desconectado")
    
    # Método legacy
    def desconectar(self):
        """Método legacy. Use disconnect() en su lugar."""
        self.disconnect()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor."""
        try:
            self.disconnect()
        except:
            pass


# Alias para mantener compatibilidad con código anterior
comunicacion = SerialCommunication

