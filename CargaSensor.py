import pandas as pd

def obtener_ultima_lectura(archivo_csv):
    """
    Función que carga un archivo CSV de datalogger y devuelve la última lectura válida
    
    Args:
        archivo_csv (str): Ruta del archivo CSV a cargar
    
    Returns:
        dict: Diccionario con los nombres de las variables y sus valores en la última lectura
              o None si hay errores
    """
    try:
        # Leer el CSV saltando las 4 primeras filas de metadatos
        datos = pd.read_csv(archivo_csv, skiprows=4)
        
        # Verificar que el archivo no esté vacío
        if datos.empty:
            print("El archivo CSV está vacío.")
            return None
            
        # Obtener los nombres de las columnas del CSV original
        with open(archivo_csv, 'r') as f:
            lineas = f.readlines()
            nombres_columnas = lineas[1].strip().split(',')
        
        # Asignar los nombres correctos a las columnas
        datos.columns = [nombre.strip('"') for nombre in nombres_columnas]
        
        # Eliminar filas con valores "NAN" (cuando el datalogger no tenía datos)
        datos = datos.replace('NAN', pd.NA).dropna()
        
        # Verificar si quedan datos válidos
        if datos.empty:
            print("No hay lecturas válidas en el archivo.")
            return None
            
        # Obtener la última fila con datos válidos
        ultima_fila = datos.iloc[-1]
        
        # Convertir a diccionario (variable: valor)
        ultima_lectura = ultima_fila.to_dict()
        
        return ultima_lectura
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_csv}")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar el archivo: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Nombre del archivo CSV
    nombre_archivo = "CR310_RK900_10.csv"
    
    # Obtener la última lectura válida
    lectura = obtener_ultima_lectura(nombre_archivo)
    
    if lectura is not None:
        print("\nÚltima lectura válida registrada:")
        print("-" * 50)
        print(f"TIMESTAMP: {lectura['TIMESTAMP']}")
        print(f"RECORD: {lectura['RECORD']}")
        print(f"Wind_Direction: {lectura['Wind_Direction']} degrees")
        print(f"Speed_Direction: {lectura['Speed_Direction']} m/s")
        print(f"Temperature: {lectura['Temperature']} °C")
        print(f"Humidity: {lectura['Humidity']}%")
        print(f"Atm_Pressure: {lectura['Atm_Pressure']} hPa")
        print(f"Radiation: {lectura['Radiation']} W/m2")
        print(f"Precipitation: {lectura['Precipitation']} mm/hr")
        print("-" * 50)