import serial, serial.tools.list_ports
from threading import Thread, Event
from tkinter import StringVar
import time as time

class comunicacion():
    def __init__(self,*args):
        super().__init__(*args)
        self.datos_recibidos = StringVar()

        self.arduino= serial.Serial()
        self.arduino.timeout=0.5

        self.baudrates = ['1200','2400','4800','9600','19200','38400','115200']
        self.puertos = []

        self.senial = Event()
        self.hilo = None
        self.status=False
    
    def puertos_disponibles(self):
        self.puertos = [port.device for port in serial.tools.list_ports.comports()]

    def conexion_serial(self):
        try:
            self.arduino.open()
        except:
            pass
        if (self.arduino.is_open):
            self.arduino.reset_input_buffer()
            self.status=True
            print('Conectado')
    
    def enviar_datos(self,data):
        if(self.arduino.is_open):
            self.datos= str(data) + "\n"

            self.arduino.write(self.datos.encode())
        else:
            print('No se enviaron los datos')

    def leer_datos(self):
        try:
            if(self.arduino.is_open):
                data= self.arduino.readline().decode("ascii").strip()
                if(len(data)>=1):
                    self.datos_recibidos.set(data)
        except TypeError:
            pass

    def iniciar_hilo(self):
        self.hilo = Thread(target= self.leer_datos)
        self.hilo.daemon=True
        self.senial.set()
        self.hilo.start()

    def stop_hilo(self):
        if(self.hilo is not None):
            self.senial.clear()
            self.hilo.join()
            self.hilo = None

    def desconectar(self):
        self.arduino.close()
        self.stop_hilo()
        self.status=False
        print('Desconectado')



