import os
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import math
import roboticstoolbox as rtb
import tkinter as tk
from ComSerial import comunicacion
import Interpretacion as intp
import threading
import time
from CTkXYFrame import *
import GPS
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image, ImageTk, ImageDraw
import io
import CargaSensor as CS





carpeta_principal = os.path.dirname(__file__)
carpeta_imagenes = os.path.join(carpeta_principal, "imagenes")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("900x600")
        self.root.title('Radar')
        wtotal = self.root.winfo_screenwidth()
        htotal = self.root.winfo_screenheight()

        wventana = 1200
        hventana = 800

        pwidth = round(wtotal / 2 - wventana / 2)
        pheight = round(htotal / 2 - hventana / 2)
        self.pantalla=0

        self.root.geometry(str(wventana) + "x" + str(hventana) + "+" + str(pwidth) + "+" + str(pheight))

        self.menu = ctk.CTkFrame(self.root, fg_color="#1F6AA5", width=220)
        self.menu.pack(side=ctk.LEFT, fill='both', expand=False)
        self.simulando=False

        self.contenedor = CTkXYFrame(self.root, fg_color="#242424",width=900,height=800)
        self.contenedor.pack(side=ctk.RIGHT, fill='both', expand=True)

        self.label = ctk.CTkLabel(self.menu, text="\nR A D A R\n", font=("Arial Black", 20), padx=30)
        self.label.pack(side=ctk.TOP)

        # Configuración frame principal
        self.icon_visualizar = ctk.CTkImage(light_image=Image.open(os.path.join(carpeta_imagenes, "Icono radar.png")),dark_image=Image.open(os.path.join(carpeta_imagenes, "Icono radar.png")), size=(50, 50))
        self.icon_control = ctk.CTkImage(light_image=Image.open(os.path.join(carpeta_imagenes, "Icono palanca.png")),dark_image=Image.open(os.path.join(carpeta_imagenes, "Icono palanca.png")), size=(50, 50))
        self.icon_fac = ctk.CTkImage(light_image=Image.open(os.path.join(carpeta_imagenes, "Icono fac.png")),dark_image=Image.open(os.path.join(carpeta_imagenes, "Icono fac.png")), size=(700,435))
        self.button_control = ctk.CTkButton(self.menu, text="Control",image=self.icon_control, width=220, command=self.pantalla_control)
        self.button_visualizar = ctk.CTkButton(self.menu, text="Visualización",image=self.icon_visualizar, width=220, command=self.pantalla_visualizacion)

       
        self.frame_logo=ctk.CTkFrame(self.contenedor)
        self.logo_fac = ctk.CTkLabel(self.frame_logo, text="", image=self.icon_fac)
        self.logo_fac.pack(ipadx=wtotal/2, ipady=htotal/5)
        self.frame_logo.grid(row=0,column=0)

        self.button_control.pack(side=ctk.TOP)
        self.button_visualizar.pack(side=ctk.TOP)
        #self.logo_fac.place(x=0,y=0,relwidth=1,relheight=1)

        self.objeto_control=None
        self.objeto_visualizacion=None

        self.serial=comunicacion()
        
        # Configurar las columnas de la cuadrícula para que se expandan
        for i in range(5):
            self.contenedor.grid_columnconfigure(i, weight=1)
        
        self.root.mainloop()


    def pantalla_control(self):

        if self.objeto_control== None:
            self.objeto_control=panel_control(self.root,self.contenedor,self.serial)
        self.objeto_control.principal.lift()
        self.pantalla=1
                 


    def pantalla_visualizacion(self):
        if (self.serial.status==True):
            if self.objeto_visualizacion==None:
                self.objeto_visualizacion=panel_visualizacion(self.root,self.contenedor,self.serial)
                self.objeto_visualizacion.iniciar()
            self.objeto_visualizacion.principal.lift()
            self.pantalla=2
        else:
            messagebox.showerror("Sin comunicacion serial","Establezca primero la comunicación serial")


    def limpiarpanel(self):
            for widget in self.principal.winfo_children():
                widget.destroy()





class panel_control:
    def __init__(self,root,contenedor,serial):
        # Configuración inicial de CustomTkinter

        self.root = root
        self.contenedor=contenedor
        

        self.principal=ctk.CTkFrame(self.contenedor,width=900,height=800)
        self.principal.grid(row=0,column=0)
        matplotlib.use('Agg')

        self.datos_arduino = serial
        self.port = self.datos_arduino.puertos
        self.baud = self.datos_arduino.baudrates

        # Frame principal
        self.framePolla = ctk.CTkFrame(self.principal, width=200, height=200)
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
        self.frameCock = ctk.CTkFrame(self.principal, width=200, height=200)
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
        self.frameControles = ctk.CTkFrame(self.principal, width=400, height=300)
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

        self.orientacion = 0

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
            self.entryGain.configure(text_color='white')
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
            self.entryGain.configure(text_color='white')
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

            if dato <= 0:
                self.datos_arduino.enviar_datos("TD" + str(abs(dato)))
                print("TU" + str(dato))
            else:
                self.datos_arduino.enviar_datos("TU" + str(abs(dato)))
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

            dato1num = int(self.slider1.get())
            dato2num = int(self.slider2.get())
            
            dato1 = str(dato1num)
            dato2 = str(dato2num)
            
            self.entry1.configure(state='normal')
            self.entry1.delete(0, ctk.END)
            self.entry1.configure(text_color='white')
            self.entry1.insert(0, dato1)
            self.entry1.configure(state='readonly')
            
            self.entry2.configure(state='normal')
            self.entry2.delete(0, ctk.END)
            self.entry2.configure(text_color='white')
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


        self.datos_arduino.arduino.port = self.combobox_port.get()
        self.datos_arduino.arduino.baudrate = self.combobox_baud.get()
        self.datos_arduino.conexion_serial()
        time.sleep(0.5)
        self.datos_arduino.arduino.reset_input_buffer()
        

        #if (1):
        if(self.datos_arduino.status==True):
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
            self.flagsliders2 = 1
            messagebox.showinfo(title="Conexión", message="Conectado al puerto serial, control habilitado.")
  

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
        messagebox.showinfo(title="Desconexión", message="Retornando a posición HOME y desconectando serial.")

    def iniciar(self):
        self.root.mainloop()


class barrido:
    def __init__(self, arregloInterpretado):
        self.radios={}
        for actual in arregloInterpretado:
            if int(actual[8]) not in self.radios:
                self.radios[int(actual[8])]=radio(actual)
        self.fallos = list(set(
            item 
            for actual in self.radios 
            for item in self.radios[actual].fallos 
            if len(self.radios[actual].fallos) > 0
        ))
        self.anuncio = list(set(
            item 
            for actual in self.radios 
            for item in self.radios[actual].anuncio_modo 
            if len(self.radios[actual].anuncio_modo) > 0
        ))
        primera_clave = next(iter(self.radios))
        self.ganancia=self.radios[primera_clave].ganancia
        self.inclinacion=self.radios[primera_clave].inclinacion
        self.operacion=self.radios[primera_clave].operacion
        self.aceptacion = 1
        if self.radios[primera_clave].aceptacion !=2:
            self.aceptacion=0
        self.rango=0
        for actual in self.radios:
            self.rango=max(self.rango,self.radios[actual].rango)
        
        if arregloInterpretado[0][0]=="00101101":
            self.tipo_vp=1
        elif arregloInterpretado[0][0]=="01111001":
            self.tipo_vp=2
            self.anuncio=list()
            self.anuncio.append(7)

class radio:
    def __init__(self,radio_arreglo):
        self.aceptacion=radio_arreglo[1]
        self.anuncio_modo=radio_arreglo[2]
        self.fallos=radio_arreglo[3]
        self.operacion=radio_arreglo[4]
        self.inclinacion=radio_arreglo[5]
        self.ganancia=radio_arreglo[6]
        self.rango=radio_arreglo[7]
        self.datos=radio_arreglo[9]
  
class grafico:
    def __init__(self):
        self.color_map ={
            0: (0, 0, 0, 0),
            1: "green",
            2: "yellow",
            3: "red",
            4: "magenta"
        }
        self.fig, self.ax= plt.subplots(subplot_kw={'polar': True}, figsize=(8.6, 7.6))
        self.lines={}
        self.num_pixels=512
        for angulo in range(-49, 50):  # Crear líneas para todos los ángulos posibles
            self.lines[angulo] = [
                self.ax.plot(
                    [   0, 0], [0, 0],  # Inicialmente vacío
                    color=(0, 0, 0, 0), lw=3, zorder=1
                )[0] for _ in range(self.num_pixels - 1)
            ]
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_thetamin(-49)
        self.ax.set_thetamax(49)
        self.ax.grid(zorder=3)
        self.ax.set_title("Datos del radar", va='bottom')
        self.barrido_actual=None
        # Configuración inicial de los grids radiales
        self.configurar_grids_radiales()



    def configurar_grids_radiales(self, rango=None, es_perfil_vertical=False):
        """Configura los grids radiales según el tipo de gráfico"""
        if rango is None:
            rango = self.barrido_actual.rango if self.barrido_actual else 100
        
        # Calculamos los intervalos adecuados para las etiquetas radiales
        if es_perfil_vertical:
            # Para perfil vertical, menos etiquetas y más espaciadas
            step = max(10, rango // 4)  # Máximo 4 etiquetas
            self.ax.set_rgrids(
                radii=np.arange(0, rango+step, step)
            )
        else:
            # Para vista normal, un poco más de etiquetas pero no demasiadas
            step = max(5, rango // 4)  # Máximo 6 etiquetas
            self.ax.set_rgrids(
                radii=np.arange(0, rango+step, step)
            )

    def actualizar_grafico(self, barrido_nuevo, lat, lon, compass):
        if barrido_nuevo.tipo_vp == 1:
            self.barrido_actual = barrido_nuevo
        
            for angulo, actual in self.barrido_actual.radios.items():
                valores = np.linspace(0, actual.rango, self.num_pixels)
                angulo_rad = np.deg2rad(angulo)
                if angulo in self.lines:
                    for i in range(len(actual.datos) - 1):
                        self.lines[angulo][i].set_data(
                            [angulo_rad, angulo_rad],
                            [valores[i], valores[i + 1]]
                        )
                        self.lines[angulo][i].set_color(self.color_map[actual.datos[i]])
            
            self.ax.set_ylim(0, self.barrido_actual.rango)
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            self.ax.set_thetamin(-49)
            self.ax.set_thetamax(49)
            angles = np.arange(-45, 46, 15) 
            self.ax.set_thetagrids(angles=angles, labels=[f"{x}°" if x != 0 else "0°" for x in angles])
            self.ax.grid(zorder=3)
            self.ax.set_title("Datos del radar", va='bottom')
            # Configurar grids para vista normal
            self.configurar_grids_radiales(self.barrido_actual.rango, False)
            self.barrido_actual = None


        elif barrido_nuevo.tipo_vp == 2:
            self.barrido_actual = barrido_nuevo

            for angulo, actual in self.barrido_actual.radios.items():
                valores = np.linspace(0, actual.rango, self.num_pixels)
                angulo_rad = -np.deg2rad(angulo)
                if angulo in self.lines:
                    for i in range(len(actual.datos) - 1):
                        self.lines[angulo][i].set_data(
                            [angulo_rad, angulo_rad],
                            [valores[i], valores[i + 1]]
                        )
                        self.lines[angulo][i].set_color(self.color_map[actual.datos[i]])
            
            self.ax.set_ylim(0, self.barrido_actual.rango)
            self.ax.set_theta_zero_location("E")
            self.ax.set_theta_direction(-1)
            self.ax.set_thetamin(-30)
            self.ax.set_thetamax(30)
            angles_vp = np.arange(-30, 31, 10) 
            self.ax.set_thetagrids(angles=angles_vp, labels=[f"{-x}°" if x != 0 else "0°" for x in angles_vp])
            self.ax.grid(zorder=3)
            self.ax.set_title("Perfil vertical", va='bottom')
            # Configurar grids para perfil vertical
            self.configurar_grids_radiales(self.barrido_actual.rango, True)
            self.barrido_actual = None










        
class panel_visualizacion:
    def __init__(self,root,contenedor,serial):
        self.root = root
        self.contenedor=contenedor
        self.principal=ctk.CTkFrame(self.contenedor,width=900,height=800)
        self.principal.grid(row=0,column=0)
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(self.principal,width=500,height=500)
        self.frame_grafico.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        
        # Frame para los indicadores
        self.frameIndicadores = ctk.CTkFrame(self.principal, width=200)
        self.frameIndicadores.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Inicializar el gráfico
        self.grafico = grafico()
        self.fig = self.grafico.fig
        self.ax  = self.grafico.ax



        # Canvas para el gráfico
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Frame para indicadores del sensor meteorologico

        self.frameSensor = ctk.CTkFrame(self.frameIndicadores, width=200)
        self.frameSensor.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configurar los widgets de los indicadores
        
        self._crear_widgets_indicadores()
        
        self.barrido_actual = None
        self.barrido_nuevo = barrido(intp.main())
        self.lock = threading.Lock()

        self.serial=serial
        self.gps1=None
        self.gps2=None
        self.compass=None




    
    def _crear_widgets_indicadores(self):
        #Crea todos los widgets de los indicadores en el frame izquierdo
        # Aceptación
        self.l_aceptacion = ctk.CTkLabel(self.frameIndicadores, text="Aceptacion", 
                                        text_color="red", font=('Arial', 12, 'bold'))
        self.l_aceptacion.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        
        # Modo de operación
        ctk.CTkLabel(self.frameIndicadores, text="Operacion:", 
                    font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=10, pady=10)
        
        self.l_STDBY = ctk.CTkLabel(self.frameIndicadores, text="STDBY", 
                                   font=('Arial', 12, 'bold'))
        self.l_STDBY.grid(row=1, column=1, padx=10, pady=10)
        
        self.l_TEST = ctk.CTkLabel(self.frameIndicadores, text="TEST", 
                                  font=('Arial', 12, 'bold'))
        self.l_TEST.grid(row=2, column=1, padx=10, pady=10)
        
        self.l_ON = ctk.CTkLabel(self.frameIndicadores, text="ON", 
                                font=('Arial', 12, 'bold'))
        self.l_ON.grid(row=3, column=1, padx=10, pady=10)
        
        # Fallos
        ctk.CTkLabel(self.frameIndicadores, text="Fallos", 
                    font=('Arial', 12, 'bold')).grid(row=4, column=0, padx=10, pady=10)
        
        self.campoFallos = ctk.CTkTextbox(self.frameIndicadores, width=180, 
                                         font=('Arial', 12, 'bold'), height=60)
        self.campoFallos.grid(row=4, column=1, padx=10, pady=10)
        self.campoFallos.insert("0.0", "iniciando")
        self.campoFallos.configure(state="disabled")
        
        # Modo especial
        ctk.CTkLabel(self.frameIndicadores, text="Modo especial", 
                    font=('Arial', 12, 'bold')).grid(row=5, column=0, padx=10, pady=10)
        
        self.campoAnuncio = ctk.CTkTextbox(self.frameIndicadores, width=180, 
                                          font=('Arial', 12, 'bold'), height=60)
        self.campoAnuncio.grid(row=5, column=1, padx=10, pady=10)
        self.campoAnuncio.insert("0.0", "iniciando")
        self.campoAnuncio.configure(state="disabled")
        
        # Rango
        ctk.CTkLabel(self.frameIndicadores, text="Rango:", 
                    font=('Arial', 12, 'bold')).grid(row=6, column=0, padx=10, pady=10)
        
        self.campoRango = ctk.CTkEntry(self.frameIndicadores, width=180, 
                                      font=('Arial', 12, 'bold'))
        self.campoRango.grid(row=6, column=1, padx=10, pady=10)
        self.campoRango.insert(0, "iniciando")
        self.campoRango.configure(state="readonly")
        
        # Ganancia
        ctk.CTkLabel(self.frameIndicadores, text="Ganancia:", 
                    font=('Arial', 12, 'bold')).grid(row=7, column=0, padx=10, pady=10)
        
        self.campoGanancia = ctk.CTkEntry(self.frameIndicadores, width=180, 
                                         font=('Arial', 12, 'bold'))
        self.campoGanancia.grid(row=7, column=1, padx=10, pady=10)
        self.campoGanancia.insert(0, "iniciando")
        self.campoGanancia.configure(state="readonly")
        
        # Inclinación
        ctk.CTkLabel(self.frameIndicadores, text="Inclinacion:", 
                    font=('Arial', 12, 'bold')).grid(row=8, column=0, padx=10, pady=10)
        
        self.campoInclinacion = ctk.CTkEntry(self.frameIndicadores, width=180, 
                                           font=('Arial', 12, 'bold'))
        self.campoInclinacion.grid(row=8, column=1, padx=10, pady=10)
        self.campoInclinacion.insert(0, "iniciando")
        self.campoInclinacion.configure(state="readonly")

        self.labelCoordenadas= ctk.CTkLabel(self.frameIndicadores, text="Coordenadas:", 
                    font=('Arial', 12, 'bold'))
        self.labelCoordenadas2= ctk.CTkLabel(self.frameIndicadores, text="0,0", 
                    font=('Arial', 12, 'bold'))
        self.labelCoordenadas.grid(row=9, column=0, padx=10, pady=10)
        self.labelCoordenadas2.grid(row=9, column=1, padx=10, pady=10)
        self.labelDir= ctk.CTkLabel(self.frameIndicadores, text="Orientación:", 
                    font=('Arial', 12, 'bold'))
        self.labelDir2= ctk.CTkLabel(self.frameIndicadores, text="0", 
                    font=('Arial', 12, 'bold'))
        self.labelDir.grid(row=10, column=0, padx=10, pady=10)
        self.labelDir2.grid(row=10, column=1, padx=10, pady=10)


        # Sensor meteorologico

        ctk.CTkLabel(self.frameSensor, text="Último dato del sensor meteorológico", 
                    font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        ctk.CTkLabel(self.frameSensor, text="Fecha y hora:", 
                    font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=10, pady=10)
        
        self.campoFecha = ctk.CTkEntry(self.frameSensor, width=180, 
                                           font=('Arial', 12, 'bold'))
        self.campoFecha.grid(row=1, column=1, padx=10, pady=10)
        self.campoFecha.insert(0, "iniciando")
        self.campoFecha.configure(state="readonly")

        ctk.CTkLabel(self.frameSensor, text="Temperatura:", 
                    font=('Arial', 12, 'bold')).grid(row=2, column=0, padx=10, pady=10)
        
        self.campoTemp = ctk.CTkEntry(self.frameSensor, width=180, 
                                           font=('Arial', 12, 'bold'))
        self.campoTemp.grid(row=2, column=1, padx=10, pady=10)
        self.campoTemp.insert(0, "iniciando")
        self.campoTemp.configure(state="readonly")

        ctk.CTkLabel(self.frameSensor, text="Direccion del viento:", 
                    font=('Arial', 12, 'bold')).grid(row=3, column=0, padx=10, pady=10)
        
        self.campoDir = ctk.CTkEntry(self.frameSensor, width=180, 
                                           font=('Arial', 12, 'bold'))
        self.campoDir.grid(row=3, column=1, padx=10, pady=10)
        self.campoDir.insert(0, "iniciando")
        self.campoDir.configure(state="readonly")

        ctk.CTkLabel(self.frameSensor, text="Nivel de precipitaciones:", 
                    font=('Arial', 12, 'bold')).grid(row=4, column=0, padx=10, pady=10)
        
        self.campoRain = ctk.CTkEntry(self.frameSensor, width=180, 
                                           font=('Arial', 12, 'bold'))
        self.campoRain.grid(row=4, column=1, padx=10, pady=10)
        self.campoRain.insert(0, "iniciando")
        self.campoRain.configure(state="readonly")



    
    def iniciar(self):
        self.root.after(1000, self.actualizar)

    def actualizar(self):
        tinicial = time.time()

        self.barrido_actual = self.barrido_nuevo
        hilo = threading.Thread(target=self.nueva_lectura, daemon=True)
        hilo.start()

        self.serial.leer_datos()
        gps1=self.serial.datos_recibidos.get()
        print(gps1)
        self.serial.leer_datos()
        gps2=self.serial.datos_recibidos.get()
        print(gps2)
        self.serial.leer_datos()
        self.compass=self.serial.datos_recibidos.get()
        print(self.compass)
        self.gps1=GPS.main(gps1)
        self.gps2=GPS.main(gps2)
        
        
        self.serial.arduino.reset_input_buffer()

        if (self.gps1.get("fix_quality")==0  or self.gps1.get("satellites_in_use")<4 or self.gps2.get("status")=='V'):
            self.latitud=0
            self.longitud=0
        else:
            self.latitud=float(self.gps1.get("latitude"))
            self.longitud=float(self.gps1.get("longitude"))  
        
        self.labelCoordenadas2.configure(text=str(round(self.latitud,5))+","+str(round(self.longitud,5)))
        self.labelDir2.configure(text=self.compass)


        self.grafico.actualizar_grafico(self.barrido_actual,self.latitud,self.longitud,self.compass)
        self.canvas.draw_idle()

        self.grafico.fig.savefig('radar.png',transparent=True)

        imagen = Image.open('radar.png')
        ancho, alto = imagen.size

        # Coordenadas del punto de rotación (ej: esquina inferior derecha)
        punto_rotacion = (441, 577)

        # Crear una nueva imagen con fondo transparente
        imagen_rotada = Image.new("RGBA", (441*2, 577*2), (0, 0, 0, 0))
        imagen_rotada.paste(imagen, (0, 0))

        # Rotar la imagen alrededor del punto
        imagen_rotada = imagen_rotada.rotate(
        -int(self.compass), 
        center=punto_rotacion,  # Pivote de rotación
        expand=False,
        fillcolor=(0, 0, 0, 0)  # Fondo transparente
        )

        imagen_rotada.save("rotada.png")

        fig2 = plt.figure(figsize=(20,20))
        ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Añadir características geográficas (offline)
        ax2.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax2.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        ax2.add_feature(cfeature.LAND, color='lightgray')
        ax2.add_feature(cfeature.OCEAN, color='lightblue')

        # Marcar la ubicación con un punto rojo
        ax2.set_extent([-79.0042, -67.8089, -4.2269, 12.4586])  # Zoom

        plt.savefig('mapa.png', dpi=100, bbox_inches='tight', pad_inches=0)
        plt.close()


        imagenmapa =Image.open('mapa.png')
        imagenrotada=Image.open("rotada.png").resize((int(ancho*0.1611),int(alto*0.1611)))
        imagenmapa.paste(imagenrotada, (0, 0),imagenrotada)

        imagenmapa.save("total.png")


        
        # Actualizar widgets según los datos
        if self.barrido_actual.aceptacion == 1:
            self.l_aceptacion.configure(text_color="green")
        else:
            self.l_aceptacion.configure(text_color="red")

        # Modo de operación
        self.l_STDBY.configure(text_color="gray")
        self.l_ON.configure(text_color="gray")
        self.l_TEST.configure(text_color="gray")
        
        if self.barrido_actual.operacion == 0:
            self.l_STDBY.configure(text_color="blue")
        elif self.barrido_actual.operacion == 1:
            self.l_ON.configure(text_color="green")
        elif self.barrido_actual.operacion == 4:
            self.l_TEST.configure(text_color="red")

        # Fallos
        self.campoFallos.configure(state="normal")
        self.campoFallos.delete("0.0", "end")
        if len(self.barrido_actual.fallos) != 0:
            for h in range(0, len(self.barrido_actual.fallos)):
                if self.barrido_actual.fallos[h] == 5:
                    self.campoFallos.insert("end", "Antena \n")
                elif self.barrido_actual.fallos[h] == 6:
                    self.campoFallos.insert("end", "Transmision \n")
        else:
            self.campoFallos.insert("end", "Sin fallos")
        self.campoFallos.configure(state="disabled")

        # Modo especial
        self.campoAnuncio.configure(state="normal")
        self.campoAnuncio.delete("0.0", "end")
        if len(self.barrido_actual.anuncio) != 0:
            if 7 in self.barrido_actual.anuncio:
                self.campoAnuncio.insert("end", "Perfil vertical \n")
            else:    
                for f in range(0, len(self.barrido_actual.anuncio)):
                    if self.barrido_actual.anuncio[f] == 0:
                        self.campoAnuncio.insert("end", "Turbulencia \n")
                    elif self.barrido_actual.anuncio[f] == 1:
                        self.campoAnuncio.insert("end", "Clima \n")
                    elif self.barrido_actual.anuncio[f] == 2:
                        self.campoAnuncio.insert("end", "Filtracion \n")
                    elif self.barrido_actual.anuncio[f] == 3:
                        self.campoAnuncio.insert("end", "Sector reducido \n")
                    elif self.barrido_actual.anuncio[f] == 4:
                        self.campoAnuncio.insert("end", "Fuera de rango \n")
        else:
            self.campoAnuncio.insert("end", "Sin modos")
        self.campoAnuncio.configure(state="disabled")

        # Actualizar campos numéricos
        self.campoGanancia.configure(state="normal")
        self.campoGanancia.delete(0, "end")
        self.campoGanancia.insert(0, f"{self.barrido_actual.ganancia} dB")
        self.campoGanancia.configure(state="readonly")

        self.campoRango.configure(state="normal")
        self.campoRango.delete(0, "end")
        self.campoRango.insert(0, self.barrido_actual.rango)
        self.campoRango.configure(state="readonly")

        self.campoInclinacion.configure(state="normal")
        self.campoInclinacion.delete(0, "end")
        self.campoInclinacion.insert(0, f"{self.barrido_actual.inclinacion}°")
        self.campoInclinacion.configure(state="readonly")

        nombre_archivo = "CR310_RK900_10.csv"
        self.datosSensor=CS.obtener_ultima_lectura(nombre_archivo)

        self.campoFecha.configure(state="normal")
        self.campoFecha.delete(0, "end")
        self.campoFecha.insert(0, self.datosSensor.get('TIMESTAMP'))
        self.campoFecha.configure(state="readonly")

        self.campoTemp.configure(state="normal")
        self.campoTemp.delete(0, "end")
        self.campoTemp.insert(0, f"{self.datosSensor.get('Temperature')} °C")
        self.campoFecha.configure(state="readonly")

        self.campoDir.configure(state="normal")
        self.campoDir.delete(0, "end")
        self.campoDir.insert(0, f"{self.datosSensor.get('Wind_Direction')} °")
        self.campoFecha.configure(state="readonly")

        self.campoRain.configure(state="normal")
        self.campoRain.delete(0, "end")
        self.campoRain.insert(0, f"{self.datosSensor.get('Precipitation')} mm")
        self.campoFecha.configure(state="readonly")

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  

        print(time.time() - tinicial)
        self.root.after(10000, self.actualizar)

    
    def nueva_lectura(self):
        ##cap.capturaDatos()
        time.sleep(5)
        with self.lock:
            self.barrido_nuevo = barrido(intp.main())


if __name__== "__main__":
    app=App()


