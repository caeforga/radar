"""
Módulo para lectura de sensores meteorológicos.

Este módulo procesa archivos CSV de dataloggers meteorológicos.
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class WeatherSensor:
    """
    Gestor para datos de sensores meteorológicos.
    
    Lee archivos CSV de dataloggers Campbell Scientific.
    """
    
    def __init__(self, csv_file: str = "CR310_RK900_10.csv"):
        """
        Inicializa el sensor meteorológico.
        
        Args:
            csv_file: Ruta al archivo CSV del datalogger.
        """
        self.csv_file = csv_file
        self._last_reading: Optional[Dict] = None
    
    def get_last_reading(self, csv_file: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene la última lectura válida del archivo CSV.
        
        Args:
            csv_file: Ruta al archivo CSV (opcional, usa el configurado si no se especifica).
            
        Returns:
            Diccionario con los valores de la última lectura o None si hay error.
        """
        file_path = csv_file or self.csv_file
        
        try:
            # Leer el CSV saltando las 4 primeras filas de metadatos
            datos = pd.read_csv(file_path, skiprows=4)
            
            # Verificar que el archivo no esté vacío
            if datos.empty:
                logger.warning(f"El archivo CSV {file_path} está vacío")
                return None
            
            # Obtener los nombres de las columnas del CSV original
            with open(file_path, 'r') as f:
                lineas = f.readlines()
                if len(lineas) < 2:
                    logger.error("Archivo CSV con formato incorrecto")
                    return None
                nombres_columnas = lineas[1].strip().split(',')
            
            # Asignar los nombres correctos a las columnas
            datos.columns = [nombre.strip('"') for nombre in nombres_columnas]
            
            # Eliminar filas con valores "NAN"
            datos = datos.replace('NAN', pd.NA).dropna()
            
            # Verificar si quedan datos válidos
            if datos.empty:
                logger.warning("No hay lecturas válidas en el archivo")
                return None
            
            # Obtener la última fila con datos válidos
            ultima_fila = datos.iloc[-1]
            
            # Convertir a diccionario
            self._last_reading = ultima_fila.to_dict()
            
            logger.debug(f"Última lectura obtenida: {self._last_reading.get('TIMESTAMP', 'N/A')}")
            return self._last_reading
            
        except FileNotFoundError:
            logger.error(f"No se encontró el archivo {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error al procesar el archivo: {e}")
            return None
    
    @property
    def last_reading(self) -> Optional[Dict]:
        """Devuelve la última lectura guardada en memoria."""
        return self._last_reading
    
    def get_temperature(self) -> Optional[float]:
        """Obtiene la temperatura de la última lectura."""
        if self._last_reading and 'Temperature' in self._last_reading:
            try:
                return float(self._last_reading['Temperature'])
            except (ValueError, TypeError):
                return None
        return None
    
    def get_wind_direction(self) -> Optional[float]:
        """Obtiene la dirección del viento de la última lectura."""
        if self._last_reading and 'Wind_Direction' in self._last_reading:
            try:
                return float(self._last_reading['Wind_Direction'])
            except (ValueError, TypeError):
                return None
        return None
    
    def get_precipitation(self) -> Optional[float]:
        """Obtiene el nivel de precipitación de la última lectura."""
        if self._last_reading and 'Precipitation' in self._last_reading:
            try:
                return float(self._last_reading['Precipitation'])
            except (ValueError, TypeError):
                return None
        return None
    
    def get_timestamp(self) -> Optional[str]:
        """Obtiene el timestamp de la última lectura."""
        if self._last_reading and 'TIMESTAMP' in self._last_reading:
            return str(self._last_reading['TIMESTAMP'])
        return None
    
    def __str__(self) -> str:
        """Representación en string del sensor."""
        if self._last_reading:
            return f"WeatherSensor(file={self.csv_file}, last_reading={self.get_timestamp()})"
        return f"WeatherSensor(file={self.csv_file}, no_data)"


# Función legacy para compatibilidad con código anterior
def obtener_ultima_lectura(archivo_csv: str) -> Optional[Dict]:
    """
    Función legacy para compatibilidad.
    
    Use WeatherSensor.get_last_reading() en su lugar.
    """
    sensor = WeatherSensor(archivo_csv)
    return sensor.get_last_reading()

