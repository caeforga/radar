import roboticstoolbox as rtb
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ComSerial import comunicacion
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


class aplicacion:
    def __init__(self):
        # Configuración inicial de CustomTkinter
        ctk.set_appearance_mode("Dark")  # Modo oscuro
        ctk.set_default_color_theme("blue")  # Tema de color
        
        self.root = ctk.CTk()
        self.xd = 0
        self.root.title("Interfaz de control de motores del radar")
        
        matplotlib.use('Agg')

        self.datos_arduino = comunicacion()
        self.port = self.datos_arduino.puertos
        self.baud = self.datos_arduino.baudrates

        # Frame principal
        self.framePolla = ctk.CTkFrame(self.root, width=200, height=200)
        self.framePolla.grid(column=0, row=0, padx=10, pady=10)
        
        # Frame para el gráfico del robot
        self.frameGG = ctk.CTkFrame(self.framePolla, width=100, height=100)
        self.robot = rtb.SerialLink([rtb.RevoluteDH(d=0.23, alpha=-np.pi/2, offset=0), 
                                    rtb.RevoluteDH(a=0.5, offset=-np.pi/2)], name='Radar')
        
        self.robot.plot([0, 0], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])
        self.fig = plt.gcf()
        self.ax = plt.gca()
        self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
        self.ax.plot([0, 1], [0, 0], [0, 0])
        
        self.frameGG.canvas.get_tk_widget().config(width=400, height=400)
        self.frameGG.canvas.draw()
        self.frameGG.canvas.get_tk_widget().grid(row=0, column=0)
        self.frameGG.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        
        # Etiqueta y slider para motor de rotación
        self.Label1 = ctk.CTkLabel(self.framePolla, text='Motor de rotación', font=('Arial', 12, 'bold'))
        self.Label1.grid(column=0, row=3, padx=10, pady=10)

        self.slider1 = ctk.CTkSlider(self.framePolla, from_=-180, to=180, orientation="horizontal", 
                                    width=750, state="disabled", command=self.actualizar_valor)
        self.slider1.set(0)
        self.slider1.grid(row=4, column=0, padx=10, pady=10)
        self.slider1.bind("<ButtonRelease-1>", self.on_scale_release)

        self.entry1 = ctk.CTkEntry(self.framePolla, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entry1.grid(row=5, column=0, padx=10, pady=10)

        # Etiqueta y slider para motor de inclinación
        self.Label2 = ctk.CTkLabel(self.framePolla, text='Motor de inclinación', font=('Arial', 12, 'bold'))
        self.Label2.grid(column=1, row=0, padx=10, pady=10)

        self.slider2 = ctk.CTkSlider(self.framePolla, from_=-60, to=60, orientation="vertical", 
                                    height=250, state="disabled", command=self.actualizar_valor)
        self.slider2.set(0)
        self.slider2.grid(row=1, column=1, padx=10, pady=10)
        self.slider2.bind("<ButtonRelease-1>", self.on_scale_release)

        self.entry2 = ctk.CTkEntry(self.framePolla, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entry2.grid(row=2, column=1, padx=10, pady=10)

        # Frame para controles de conexión serial
        self.frameCock = ctk.CTkFrame(self.root, width=200, height=200)
        self.frameCock.grid(column=1, row=0, rowspan=2, padx=10, pady=10)

        self.LabelPuertos = ctk.CTkLabel(self.frameCock, text='Puertos COM', font=('Arial', 12, 'bold'))
        self.LabelPuertos.grid(row=3, column=0, padx=10, pady=10)
        
        self.combobox_port = ctk.CTkComboBox(self.frameCock, justify='center', width=120, font=('Arial', 12))
        self.actualizar_puertos()
        self.combobox_port.grid(row=4, column=0, pady=10, padx=10)

        self.LabelBaud = ctk.CTkLabel(self.frameCock, text='Baud Rate', font=('Arial', 12, 'bold'))
        self.LabelBaud.grid(row=5, column=0, padx=10, pady=10)
        
        self.combobox_baud = ctk.CTkComboBox(self.frameCock, values=self.baud, justify='center', 
                                           width=120, font=('Arial', 12))
        self.combobox_baud.grid(row=6, column=0, pady=10, padx=10)
        self.combobox_baud.set("9600")

        self.bt_conectar = ctk.CTkButton(self.frameCock, text='Conectar', font=('Arial', 12, 'bold'), 
                                       width=120, fg_color='green', command=self.conectar_serial)
        self.bt_conectar.grid(row=7, column=0, pady=10, padx=10)

        self.bt_actualizar = ctk.CTkButton(self.frameCock, text='Actualizar', font=('Arial', 12, 'bold'), 
                                         width=120, fg_color='magenta', command=self.actualizar_puertos)
        self.bt_actualizar.grid(row=8, column=0, pady=10, padx=10)

        self.bt_desconectar = ctk.CTkButton(self.frameCock, text='Desconectar', font=('Arial', 12, 'bold'), 
                                          width=120, fg_color='red', command=self.desconectar_serial, 
                                          state='disabled')
        self.bt_desconectar.grid(row=9, column=0, pady=10, padx=10)

        # Frame para controles de operación
        self.frameControles = ctk.CTkFrame(self.root, width=400, height=300)
        self.frameControles.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.frameOperacion = ctk.CTkFrame(self.frameControles, width=100, height=300)
        self.frameOperacion.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
        
        self.labelOperacion = ctk.CTkLabel(self.frameOperacion, text='Operación:', font=('Arial', 12, 'bold'))
        self.labelOperacion.grid(row=0, column=0, padx=10, pady=10)
        
        self.labelEncendido = ctk.CTkLabel(self.frameOperacion, text='OFF', text_color='red', 
                                         font=('Arial', 12, 'bold'))
        self.labelEncendido.grid(row=0, column=1, padx=10, pady=10)

        self.botonOFF = ctk.CTkButton(self.frameOperacion, text='Apagar', font=('Arial', 12, 'bold'), 
                                    width=120, fg_color='red', command=self.apagarRadar, state='disabled')
        self.botonOFF.grid(row=2, column=0, padx=10, pady=10)
        
        self.botonStandby = ctk.CTkButton(self.frameOperacion, text='Standby', font=('Arial', 12, 'bold'), 
                                        width=120, fg_color='blue', command=self.modoStandby, state='disabled')
        self.botonStandby.grid(row=1, column=1, padx=10, pady=10)
        
        self.botonTEST = ctk.CTkButton(self.frameOperacion, text='TEST', font=('Arial', 12, 'bold'), 
                                      width=120, fg_color='orange', command=self.modoTEST, state='disabled')
        self.botonTEST.grid(row=2, column=1, padx=10, pady=10)
        
        self.botonON = ctk.CTkButton(self.frameOperacion, text='ON', font=('Arial', 12, 'bold'), 
                                    width=120, fg_color='green', command=self.modoON, state='disabled')
        self.botonON.grid(row=3, column=1, padx=10, pady=10)
        
        # Frame para sliders de inclinación y ganancia
        self.frameSliders = ctk.CTkFrame(self.frameControles, width=200, height=300)
        self.frameSliders.grid(row=0, column=1, padx=10, pady=10)

        self.LabelInclinacion = ctk.CTkLabel(self.frameSliders, text='Inclinación', font=('Arial', 12, 'bold'))
        self.LabelInclinacion.grid(row=0, column=0, padx=10, pady=10)
        
        self.sliderInclinacion = ctk.CTkSlider(self.frameSliders, from_=-15, to=15, orientation="horizontal", 
                                             width=200, state="disabled", command=self.actualizar_inclinacion)
        self.sliderInclinacion.set(0)
        self.sliderInclinacion.grid(row=1, column=0, padx=10, pady=10)

        self.entryInclinacion = ctk.CTkEntry(self.frameSliders, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entryInclinacion.grid(row=2, column=0, padx=10, pady=10)

        self.LabelGain = ctk.CTkLabel(self.frameSliders, text='Ganancia', font=('Arial', 12, 'bold'))
        self.LabelGain.grid(row=0, column=1, padx=10, pady=10)
        
        self.sliderGain = ctk.CTkSlider(self.frameSliders, from_=-31.5, to=0, orientation="horizontal", 
                                       width=200, state="disabled", command=self.proximo_gain)
        self.sliderGain.set(0)
        self.sliderGain.grid(row=1, column=1, padx=10, pady=10)
        self.sliderGain.bind("<ButtonRelease-1>", self.actualizar_gain)

        self.entryGain = ctk.CTkEntry(self.frameSliders, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entryGain.grid(row=2, column=1, padx=10, pady=10)

        # Frame para botones de control
        self.frameBotones = ctk.CTkFrame(self.frameControles, width=200, height=300)
        self.frameBotones.grid(row=0, column=2, padx=10, pady=10)

        self.botonRNGarriba = ctk.CTkButton(self.frameBotones, text='RNG ▲', font=('Arial', 12, 'bold'), 
                                           width=120, fg_color='yellow', text_color='black', 
                                           command=self.rangoArriba, state='disabled')
        self.botonRNGarriba.grid(row=2, column=1, padx=10, pady=10)
        
        self.botonRNGabajo = ctk.CTkButton(self.frameBotones, text='RNG ▼', font=('Arial', 12, 'bold'), 
                                          width=120, fg_color='yellow', text_color='black', 
                                          command=self.rangoAbajo, state='disabled')
        self.botonRNGabajo.grid(row=3, column=1, padx=10, pady=10)

        self.botonVp = ctk.CTkButton(self.frameBotones, text='VP', font=('Arial', 12, 'bold'), 
                                    width=120, fg_color='red', command=self.perfilVertical, state='disabled')
        self.botonVp.grid(row=4, column=1, columnspan=4, padx=10, pady=10)

        self.botonTRKizquierda = ctk.CTkButton(self.frameBotones, text='TRK ◄', font=('Arial', 12, 'bold'), 
                                              width=120, fg_color='blue', command=self.trakerIzquierda, state='disabled')
        self.botonTRKizquierda.grid(row=2, column=3, padx=10, pady=10)

        self.botonTRKderecha = ctk.CTkButton(self.frameBotones, text='TRK ►', font=('Arial', 12, 'bold'), 
                                            width=120, fg_color='blue', command=self.trakerDerecha, state='disabled')
        self.botonTRKderecha.grid(row=3, column=3, padx=10, pady=10)
        
        self.entryTrack = ctk.CTkEntry(self.frameBotones, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entryTrack.grid(row=2, column=4, rowspan=2, padx=10, pady=10)

        self.entryRNG = ctk.CTkEntry(self.frameBotones, width=50, font=('Arial', 12, 'bold'), state='disabled')
        self.entryRNG.grid(row=2, column=0, rowspan=2, padx=10, pady=10)

        self.anguloTrack = 0
        self.rango = 80
        self.perfil = 0

        self.flag = 0
        self.flagsliders1 = 0
        self.flagsliders2 = 0

    # Los métodos de la clase permanecen iguales, ya que la lógica no cambia
    def modoStandby(self):
        self.botonOFF.configure(state='normal')
        self.botonStandby.configure(state='disabled')
        self.botonTEST.configure(state='normal')
        self.botonON.configure(state='disabled')
        self.labelEncendido.configure(text_color='blue', text='Standby')
        self.bt_desconectar.configure(state='disabled')
        
        self.sliderInclinacion.set(0)
        self.sliderGain.set(0)

        self.entryInclinacion.configure(state='normal')
        self.entryGain.configure(state='normal')
        
        self.entryInclinacion.delete(0, ctk.END)
        self.entryGain.delete(0, ctk.END)
        self.entryInclinacion.insert(0, '0')
        self.entryGain.insert(0, '0')
        
        self.entryInclinacion.configure(state='readonly')
        self.entryGain.configure(text_color='gray')
        self.entryGain.configure(state='readonly')

        self.sliderInclinacion.configure(state='disabled')
        self.sliderGain.configure(state='disabled')
        
        self.entryInclinacion.configure(state='disabled')
        self.entryGain.configure(state='disabled')

        self.botonRNGabajo.configure(state='disabled')
        self.botonRNGarriba.configure(state='disabled')
        self.botonVp.configure(state='disabled')

        self.entryRNG.configure(state='disabled')
        
        self.flag = 0
        self.flagsliders1 = 0

        self.datos_arduino.enviar_datos("sby")

    def modoTEST(self):
        self.botonOFF.configure(state='disabled')
        self.botonStandby.configure(state='normal')
        self.botonTEST.configure(state='disabled')
        self.botonON.configure(state='normal')
        self.labelEncendido.configure(text_color='orange', text='TEST')
        self.sliderInclinacion.configure(state='normal')
        self.sliderGain.configure(state='normal')
        self.entryInclinacion.configure(state='normal')
        self.entryGain.configure(state='normal')
        self.botonTRKderecha.configure(state='disabled')
        self.botonTRKizquierda.configure(state='disabled')

        self.entryTrack.configure(state='disabled')
       
        if self.flag == 0:
            self.entryGain.delete(0, ctk.END)
            self.entryInclinacion.delete(0, ctk.END)
            self.entryInclinacion.insert(0, '0')
            self.entryGain.insert(0, '0')
            self.entryGain.configure(text_color='black')
            self.entryInclinacion.configure(state='readonly')
            self.entryGain.configure(state='readonly')
            self.sliderGain.set(0)
            self.sliderInclinacion.set(0)
            self.botonRNGabajo.configure(state='normal')
            self.botonRNGarriba.configure(state='normal')
            self.botonVp.configure(state='normal')

            self.entryRNG.configure(state='normal')
            self.entryRNG.delete(0, ctk.END)
            self.entryRNG.insert(0, str(self.rango))
            self.entryRNG.configure(state='readonly')

            self.flag = 1
            self.flagsliders1 = 1

        self.datos_arduino.enviar_datos("tst")

    def modoON(self):
        self.botonOFF.configure(state='disabled')
        self.botonStandby.configure(state='disabled')
        self.botonTEST.configure(state='normal')
        self.botonON.configure(state='disabled')
        self.labelEncendido.configure(text_color='green', text='ON')

        self.botonTRKderecha.configure(state='normal')
        self.botonTRKizquierda.configure(state='normal')

        self.entryTrack.configure(state='normal')
        self.entryTrack.delete(0, ctk.END)
        self.entryTrack.insert(0, str(self.anguloTrack))
        self.entryTrack.configure(state='readonly')

        self.datos_arduino.enviar_datos("on")

    def apagarRadar(self):
        self.botonOFF.configure(state='disabled')
        self.botonStandby.configure(state='normal')
        self.botonTEST.configure(state='disabled')
        self.botonON.configure(state='disabled')
        self.labelEncendido.configure(text_color='red', text='OFF')
        self.bt_desconectar.configure(state='normal')
        self.datos_arduino.enviar_datos("off")

    def proximo_gain(self, value):
        if self.flagsliders1 == 1:
            dato = round(value * 2) / 2
            self.sliderGain.set(dato)
            self.entryGain.configure(state='normal')
            self.entryGain.configure(text_color='red')
            self.entryGain.delete(0, ctk.END)
            self.entryGain.insert(0, dato)
            self.entryGain.configure(state='readonly')

    def actualizar_gain(self, event):
        if self.flagsliders1 == 1:
            value = self.sliderGain.get()
            dato = round(value * 2) / 2
            self.sliderGain.set(dato)
            self.entryGain.configure(state='normal')
            self.entryGain.configure(text_color='black')
            self.entryGain.delete(0, ctk.END)
            self.entryGain.insert(0, dato)
            self.entryGain.configure(state='readonly')

            self.datos_arduino.enviar_datos("G" + str(int(dato)))

    def actualizar_inclinacion(self, value):
        if self.flagsliders1 == 1:
            dato = round(value * 4) / 4
            self.sliderInclinacion.set(dato)
            self.entryInclinacion.configure(state='normal')
            self.entryInclinacion.delete(0, ctk.END)
            self.entryInclinacion.insert(0, dato)
            self.entryInclinacion.configure(state='readonly')
            print('holaaa')
            #self.xd=self.xd+0.2

            if dato <= 0:
                self.xd = self.xd + 0.2
                self.datos_arduino.enviar_datos("TU" + str(abs(dato)))  # "TU"+str(dato)     "TU"+str(self.xd)
                print("TU" + str(dato))
            else:
                self.xd = self.xd - 0.2
                self.datos_arduino.enviar_datos("TD" + str(abs(dato)))  # "TD"+str(-dato)      "TD"+str(-1*(self.xd))
                print("TD" + str(dato))

    def rangoArriba(self):
        if self.rango < 160:
            self.rango = self.rango * 2
        elif self.rango == 160:
            self.rango = 240
        
        self.entryRNG.configure(state='normal')
        self.entryRNG.delete(0, ctk.END)
        self.entryRNG.insert(0, str(int(self.rango)))
        self.entryRNG.configure(state='readonly')
        if self.rango <= 240:
            self.datos_arduino.enviar_datos("rng_arriba")

    def rangoAbajo(self):
        if self.rango < 240 and self.rango > 10:
            self.rango = self.rango / 2
        elif self.rango == 240:
            self.rango = 160
        
        self.entryRNG.configure(state='normal')
        self.entryRNG.delete(0, ctk.END)
        self.entryRNG.insert(0, str(int(self.rango)))
        self.entryRNG.configure(state='readonly')
        if self.rango >= 10:
            self.datos_arduino.enviar_datos("rng_abajo")

    def perfilVertical(self):
        if self.perfil == 0:
            self.perfil = 1
            self.botonVp.configure(fg_color='green')
        else:
            self.perfil = 0
            self.botonVp.configure(fg_color='red')

        self.datos_arduino.enviar_datos("vp")

    def trakerIzquierda(self):
        if self.anguloTrack > -45:
            self.anguloTrack = self.anguloTrack - 1
            self.entryTrack.configure(state='normal')
            self.entryTrack.delete(0, ctk.END)
            self.entryTrack.insert(0, str(self.anguloTrack))
            self.entryTrack.configure(state='readonly')
            self.datos_arduino.enviar_datos("trk_izquierda")

    def trakerDerecha(self):
        if self.anguloTrack < 45:
            self.anguloTrack = self.anguloTrack + 1
            self.entryTrack.configure(state='normal')
            self.entryTrack.delete(0, ctk.END)
            self.entryTrack.insert(0, str(self.anguloTrack))
            self.entryTrack.configure(state='readonly')
            self.datos_arduino.enviar_datos("trk_derecha")

    def actualizar_valor(self, value):
        if self.flagsliders2 == 1:
            # Para manejar ambos sliders, necesitamos determinar cuál está generando el evento
            if hasattr(self, 'last_slider'):
                if self.last_slider == 'slider1':
                    dato2 = str(int(self.slider2.get()))
                    self.entry2.configure(state='normal')
                    self.entry2.configure(text_color='red')
                    self.entry2.delete(0, ctk.END)
                    self.entry2.insert(0, dato2)
                    self.entry2.configure(state='readonly')
                else:
                    dato1 = str(int(self.slider1.get()))
                    self.entry1.configure(state='normal')
                    self.entry1.configure(text_color='red')
                    self.entry1.delete(0, ctk.END)
                    self.entry1.insert(0, dato1)
                    self.entry1.configure(state='readonly')
            else:
                # Actualizar ambos si no sabemos cuál generó el evento
                dato1 = str(int(self.slider1.get()))
                dato2 = str(int(self.slider2.get()))
                
                self.entry1.configure(state='normal')
                self.entry1.configure(text_color='red')
                self.entry1.delete(0, ctk.END)
                self.entry1.insert(0, dato1)
                self.entry1.configure(state='readonly')
                
                self.entry2.configure(state='normal')
                self.entry2.configure(text_color='red')
                self.entry2.delete(0, ctk.END)
                self.entry2.insert(0, dato2)
                self.entry2.configure(state='readonly')

    def on_scale_release(self, event):
        if self.flagsliders2 == 1:
            # Determinar qué slider generó el evento
            if event.widget == self.slider1:
                self.last_slider = 'slider1'
                dato1num = int(self.slider1.get())
                dato2num = int(self.slider2.get())
            else:
                self.last_slider = 'slider2'
                dato1num = int(self.slider1.get())
                dato2num = int(self.slider2.get())
            
            dato1 = str(dato1num)
            dato2 = str(dato2num)
            
            self.entry1.configure(state='normal')
            self.entry1.delete(0, ctk.END)
            self.entry1.configure(text_color='black')
            self.entry1.insert(0, dato1)
            self.entry1.configure(state='readonly')
            
            self.entry2.configure(state='normal')
            self.entry2.delete(0, ctk.END)
            self.entry2.configure(text_color='black')
            self.entry2.insert(0, dato2)
            self.entry2.configure(state='readonly')
            
            self.datos_arduino.enviar_datos("M" + str(dato2) + "," + str(dato1))
            
            elev = self.ax.elev
            azim = self.ax.azim
            plt.close(self.fig)  # Cerrar la figura anterior para liberar memoria
            
            self.robot.plot([np.deg2rad(dato1num), np.deg2rad(dato2num)], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])
            self.fig = plt.gcf()
            self.ax = plt.gca()

            # Crear un nuevo canvas y agregarlo al frame
            self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
            self.ax.plot([0, 1], [0, 0], [0, 0])
            self.ax.view_init(elev=elev, azim=azim)
            self.frameGG.canvas.get_tk_widget().config(width=400, height=400)
            self.frameGG.canvas.draw()
            self.frameGG.canvas.get_tk_widget().grid(row=0, column=0)

    def actualizar_puertos(self):
        self.combobox_port.configure(state='normal')
        self.datos_arduino.puertos_disponibles()
        self.port = self.datos_arduino.puertos
        self.combobox_port.configure(values=self.port)
        self.combobox_port.set(self.port[0] if self.port else "")
        self.combobox_port.configure(state='readonly')

    def conectar_serial(self):
        self.slider1.configure(state='normal')
        self.entry1.configure(state='normal')
        self.bt_actualizar.configure(state='disabled')
        self.bt_conectar.configure(state='disabled')
        self.bt_desconectar.configure(state='normal')
        self.slider2.configure(state='normal')
        self.entry2.configure(state='normal')
        self.entry1.delete(0, ctk.END)
        self.entry2.delete(0, ctk.END)

        self.entry1.insert(0, '0')
        self.entry2.insert(0, '0')
        self.entry1.configure(state='readonly')
        self.entry2.configure(state='readonly')

        self.botonStandby.configure(state='normal')

        self.datos_arduino.arduino.port = self.combobox_port.get()
        self.datos_arduino.arduino.baudrate = self.combobox_baud.get()
        self.datos_arduino.conexion_serial()
        self.flagsliders2 = 1
        ctk.CTkMessagebox(title="Conexión", message="Conectado al puerto serial, control habilitado.")

    def desconectar_serial(self):
        self.entry1.configure(state='normal')
        self.entry1.delete(0, ctk.END)
        self.entry1.insert(0, '0')
        self.entry1.configure(state='readonly')
        
        self.entry2.configure(state='normal')
        self.entry2.delete(0, ctk.END)
        self.entry2.insert(0, '0')
        self.entry2.configure(state='readonly')
        
        self.slider1.set(0)
        self.slider2.set(0)

        self.slider1.configure(state='disabled')
        self.entry1.configure(state='disabled')

        self.slider2.configure(state='disabled')
        self.entry2.configure(state='disabled')

        self.bt_actualizar.configure(state='normal')
        self.bt_conectar.configure(state='normal')
        self.bt_desconectar.configure(state='disabled')

        self.botonStandby.configure(state='disabled')

        self.datos_arduino.enviar_datos("0,0")
        self.datos_arduino.desconectar()

        plt.close(self.fig)  # Cerrar la figura anterior para liberar memoria
        self.robot.plot([0, 0], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])

        self.fig = plt.gcf()
        self.ax = plt.gca()

        # Crear un nuevo canvas y agregarlo al frame
        self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
        self.ax.plot([0, 1], [0, 0], [0, 0])
        self.frameGG.canvas.get_tk_widget().config(width=400, height=400)
        self.frameGG.canvas.draw()
        self.frameGG.canvas.get_tk_widget().grid(row=0, column=0)
        self.flagsliders2 = 0
        ctk.CTkMessagebox(title="Desconexión", message="Retornando a posición HOME y desconectando serial.")

    def iniciar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = aplicacion()
    app.iniciar()