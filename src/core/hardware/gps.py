"""
Módulo para procesar datos GPS en formato NMEA.

Este módulo parsea tramas NMEA ($GNGGA y $GNRMC) y extrae
información de posicionamiento.
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GPSParser:
    """
    Parser para tramas NMEA GPS.
    
    Soporta las tramas $GNGGA y $GNRMC.
    """
    
    @staticmethod
    def parse_nmea(sentence: str) -> Dict[str, any]:
        """
        Analiza tramas NMEA ($GNGGA y $GNRMC).
        
        Args:
            sentence: Trama NMEA completa.
            
        Returns:
            Diccionario con los datos extraídos.
        """
        data = {}
        
        try:
            # Parseo de $GNGGA
            if sentence.startswith("$GNGGA"):
                data = GPSParser._parse_gga(sentence)
            # Parseo de $GNRMC
            elif sentence.startswith("$GNRMC"):
                data = GPSParser._parse_rmc(sentence)
            else:
                logger.warning(f"Formato NMEA no reconocido: {sentence[:7]}")
        except Exception as e:
            logger.error(f"Error al parsear NMEA: {e}")
        
        return data
    
    @staticmethod
    def _parse_gga(sentence: str) -> Dict[str, any]:
        """Parsea trama $GNGGA."""
        data = {}
        fields = sentence.split(",")
        
        if len(fields) >= 10:
            # Hora (UTC)
            data["time"] = GPSParser._convert_to_gmt_minus_5(fields[1]) if fields[1] else None
            # Coordenadas
            data["latitude"] = GPSParser._nmea_to_decimal(fields[2], fields[3]) if fields[2] else None
            data["longitude"] = GPSParser._nmea_to_decimal(fields[4], fields[5]) if fields[4] else None
            data["altitude"] = f"{fields[9]} {fields[10]}" if fields[9] else None
            # Info de satélites y fix
            data["fix_quality"] = int(fields[6]) if fields[6] else 0
            data["satellites_in_use"] = int(fields[7]) if fields[7] else 0
        
        return data
    
    @staticmethod
    def _parse_rmc(sentence: str) -> Dict[str, any]:
        """Parsea trama $GNRMC."""
        data = {}
        fields = sentence.split(",")
        
        if len(fields) >= 10:
            data["time"] = GPSParser._convert_to_gmt_minus_5(fields[1]) if fields[1] else None
            data["date"] = fields[9] if fields[9] else None
            data["status"] = fields[2]  # 'A' = Válido, 'V' = Inválido
            
            if fields[2] == "A":  # Solo si el status es válido
                data["latitude"] = GPSParser._nmea_to_decimal(fields[3], fields[4]) if fields[3] else None
                data["longitude"] = GPSParser._nmea_to_decimal(fields[5], fields[6]) if fields[5] else None
        
        return data
    
    @staticmethod
    def _nmea_to_decimal(coord: str, direction: str) -> Optional[float]:
        """
        Convierte coordenadas NMEA (grados y minutos) a decimal.
        
        Args:
            coord: Coordenada en formato NMEA (ej: "4807.038").
            direction: Dirección (N, S, E, W).
            
        Returns:
            Coordenada en formato decimal.
        """
        if not coord or not direction:
            return None
        
        # Formato: "4807.038" -> 48°07.038'
        match = re.match(r"(\d+)(\d\d\.\d+)", coord)
        if not match:
            return None
        
        degrees = int(match.group(1))
        minutes = float(match.group(2))
        decimal = degrees + (minutes / 60)
        
        # Aplicar dirección
        if direction in ('S', 'W'):
            decimal = -decimal
        
        return round(decimal, 6)
    
    @staticmethod
    def _convert_to_gmt_minus_5(utc_time: str) -> Optional[str]:
        """
        Convierte hora UTC a GMT-5.
        
        Args:
            utc_time: Hora en formato HHMMSS.sss.
            
        Returns:
            Hora en formato HH:MM:SS (GMT-5).
        """
        if not utc_time or len(utc_time) < 6:
            return None
        
        try:
            hours = int(utc_time[:2])
            minutes = int(utc_time[2:4])
            seconds = int(utc_time[4:6])
            
            # Crear objeto datetime y restar 5 horas
            utc_datetime = datetime(2000, 1, 1, hours, minutes, seconds)
            local_datetime = utc_datetime - timedelta(hours=5)
            
            return local_datetime.strftime("%H:%M:%S")
        except (ValueError, IndexError) as e:
            logger.error(f"Error al convertir hora: {e}")
            return None


# Función legacy para compatibilidad
def parse_nmea(sentence: str) -> Dict[str, any]:
    """Función legacy. Use GPSParser.parse_nmea() en su lugar."""
    return GPSParser.parse_nmea(sentence)


def main(sentence: str) -> Dict[str, any]:
    """Función legacy. Use GPSParser.parse_nmea() en su lugar."""
    return GPSParser.parse_nmea(sentence)

