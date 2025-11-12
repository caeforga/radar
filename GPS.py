import re
from datetime import datetime, timedelta

def parse_nmea(sentence):
    """
    Analiza tramas NMEA ($GNGGA y $GNRMC) y extrae:
    - Hora, fecha, latitud, longitud, altitud (si están disponibles).
    - Número de satélites usados y calidad del fix.
    - Estado de la conexión (Válido/Inválido).
    """
    data = {}
    
    # Parseo de $GNGGA
    if sentence.startswith("$GNGGA"):
        fields = sentence.split(",")
        if len(fields) >= 10:
            # Hora (UTC)
            data["time"] = convert_to_gmt_minus_5(fields[1]) if fields[1] else None
            # Coordenadas (si existen)
            data["latitude"] = nmea_to_decimal(fields[2], fields[3]) if fields[2] else None
            data["longitude"] = nmea_to_decimal(fields[4], fields[5]) if fields[4] else None
            data["altitude"] = f"{fields[9]} {fields[10]}" if fields[9] else None
            # Info de satélites y fix
            data["fix_quality"] = int(fields[6]) if fields[6] else 0  # 0 = Sin fix
            data["satellites_in_use"] = int(fields[7]) if fields[7] else 0  # Número de satélites
            
    # Parseo de $GNRMC
    elif sentence.startswith("$GNRMC"):
        fields = sentence.split(",")
        if len(fields) >= 10:
            data["time"] = convert_to_gmt_minus_5(fields[1]) if fields[1] else None
            data["date"] = fields[9] if fields[9] else None  # Fecha (DDMMYY)
            data["status"] = fields[2]  # 'A' = Válido, 'V' = Inválido
            if fields[2] == "A":  # Solo si el status es válido
                data["latitude"] = nmea_to_decimal(fields[3], fields[4]) if fields[3] else None
                data["longitude"] = nmea_to_decimal(fields[5], fields[6]) if fields[5] else None
    
    return data


def nmea_to_decimal(coord, direction):
    """
    Convierte coordenadas NMEA (grados y minutos) a decimal.
    """
    if not coord or not direction:
        return None
    # Grados y minutos: Ejemplo "4807.038" -> 48°07.038'
    match = re.match(r"(\d+)(\d\d\.\d+)", coord)
    if not match:
        return None
    degrees = int(match[1])  # Parte de grados
    minutes = float(match[2])  # Parte de minutos
    decimal = degrees + (minutes / 60)
    if direction in ["S", "W"]:
        decimal *= -1  # Coordenadas sur y oeste son negativas
    return decimal


def convert_to_gmt_minus_5(utc_time):
    """
    Convierte la hora UTC en formato HHMMSS.00 (NMEA) a GMT-5 en formato HH:MM:SS.
    """
    try:
        # Eliminar la parte decimal (.00)
        utc_time = utc_time.split(".")[0]  # Tomar solo la parte antes del punto
        # Parsear la hora UTC (HHMMSS)
        utc_datetime = datetime.strptime(utc_time, "%H%M%S")
        # Ajustar a GMT-5
        gmt_minus_5 = utc_datetime - timedelta(hours=5)
        return gmt_minus_5.strftime("%H:%M:%S")  # Retorna en formato HH:MM:SS
    except ValueError:
        return None  # Si el formato no es correcto


def main(linea):
    data1 = parse_nmea(linea)
    return(data1)

if __name__ == "__main__":
    main()
