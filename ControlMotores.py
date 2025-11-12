import roboticstoolbox as rtb
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ComSerial import comunicacion
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


class aplicacion:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interfaz de control de motores del radar")
        self.root.config(bg="black")
        matplotlib.use('Agg')

        self.datos_arduino = comunicacion()
        self.port=self.datos_arduino.puertos
        self.baud=self.datos_arduino.baudrates
        self.s=ttk.Style()
        self.s.configure('Frame1.TFrame',background='black')

        self.framePolla = ttk.Frame(self.root,style='Frame1.TFrame',width=200,height=200)
        self.framePolla.grid(column=0,row=0,padx=10,pady=10)
        self.frameGG=ttk.Frame(self.framePolla,style='Frame1.TFrame',width=100,height=100)
        self.robot= rtb.SerialLink([rtb.RevoluteDH(d=0.23, alpha= -np.pi/2, offset= 0), rtb.RevoluteDH(a= 0.5, offset= -np.pi/2)],name='Radar')
        
        self.robot.plot([0, 0], limits=[-0.5,0.5,-0.5,0.5,0,0.8])
        self.fig=plt.gcf()
        self.ax=plt.gca()
        self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
        self.ax.plot([0,1],[0,0],[0,0])
        
        self.frameGG.canvas.get_tk_widget().config(width=400,height=400)
        self.frameGG.canvas.draw()
        self.frameGG.canvas.get_tk_widget().grid(row=0,column=0)
        self.frameGG.grid(row=0,column=0,rowspan=3,padx=10,pady=10)
        self.Label1=tk.Label(self.framePolla, text='Motor de rotación', bg='black', fg='white', font=('Arial',12,'bold'))
        self.Label1.grid(column=0,row=3,padx=10,pady=10)

        self.estilo = ttk.Style()
        self.estilo.configure("Horizontal.TScale", background='black')

        self.slider1=ttk.Scale(self.framePolla, state='disabled', to=180, from_ =-180, orient='horizontal', length=750, style='TScale', value=0)
        self.slider1.grid(row=4,column=0,padx=10,pady=10)
        self.slider1.bind("<ButtonRelease-1>", self.on_scale_release)
        self.slider1.bind("<B1-Motion>", self.actualizar_valor)

        self.entry1=ttk.Entry(self.framePolla, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entry1.grid(row=5,column=0,padx=10,pady=10)

        self.Label2=tk.Label(self.framePolla, text='Motor de inclinación', bg='black', fg='white', font=('Arial',12,'bold'))
        self.Label2.grid(column=1,row=0,padx=10,pady=10)

        self.estilo2 = ttk.Style()
        self.estilo2.configure("Vertical.TScale", background='black')

        self.slider2=ttk.Scale(self.framePolla, state='disabled', to=60, from_ =-60, orient='vertical', length=250, style='TScale', value=0)
        self.slider2.grid(row=1,column=1,padx=10,pady=10)
        self.slider2.bind("<ButtonRelease-1>", self.on_scale_release)
        self.slider2.bind("<B1-Motion>", self.actualizar_valor)

        self.entry2=ttk.Entry(self.framePolla, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entry2.grid(row=2,column=1,padx=10,pady=10)

        self.frameCock=ttk.Frame(self.root,style='Frame1.TFrame',width=200,height=200)
        self.frameCock.grid(column=1,row=0,rowspan=2,padx=10,pady=10)

        self.LabelPuertos=tk.Label(self.frameCock, text='Puertos COM', bg='black', fg='white', font=('Arial',12,'bold'))
        self.LabelPuertos.grid(row=3,column=0,padx=10,pady=10)
        self.combobox_port= ttk.Combobox(self.frameCock, justify='center',width=12,font='Arial')
        self.actualizar_puertos()
        self.combobox_port.grid(row=4,column=0,pady=10, padx=10)

        self.LabelBaud=tk.Label(self.frameCock, text='Baud Rate', bg='black', fg='white', font=('Arial',12,'bold'))
        self.LabelBaud.grid(row=5,column=0,padx=10,pady=10)
        self.combobox_baud= ttk.Combobox(self.frameCock, values= self.baud, justify='center',width=12,font='Arial')
        self.combobox_baud.grid(row=6,column=0,pady=10, padx=10)
        self.combobox_baud.current(3)

        self.bt_conectar = tk.Button(self.frameCock, text='Conectar', font=('Arial',12,'bold'), width=12, bg='green2',fg='white', command=self.conectar_serial)
        self.bt_conectar.grid(row=7,column=0,pady=10, padx=10)

        self.bt_actualizar = tk.Button(self.frameCock, text='Actualizar', font=('Arial',12,'bold'), width=12, bg='magenta',fg='white', command=self.actualizar_puertos )
        self.bt_actualizar.grid(row=8,column=0,pady=10, padx=10)

        self.bt_desconectar = tk.Button(self.frameCock, text='Desconectar', font=('Arial',12,'bold'), width=12, bg='red2',fg='white', command=self.desconectar_serial, state='disabled')
        self.bt_desconectar.grid(row=9,column=0,pady=10, padx=10)


        self.frameControles= ttk.Frame(self.root, style='Frame1.TFrame', width=400, height=300)
        self.frameControles.grid(row=1,column=0,columnspan=2,padx=10,pady=10)

        self.frameOperacion= ttk.Frame(self.frameControles, style='Frame1.TFrame', width=100, height=300)
        self.frameOperacion.grid(row=0,column=0,rowspan=4,padx=10,pady=10)
        
        self.labelOperacion=tk.Label(self.frameOperacion, text='Operación:', bg='black', fg='white', font=('Arial',12,'bold'))
        self.labelOperacion.grid(row=0, column=0, padx=10, pady=10)
        self.labelEncendido=tk.Label(self.frameOperacion, text='OFF', bg='black', fg='red', font=('Arial',12,'bold'))
        self.labelEncendido.grid(row=0, column=1, padx=10,pady=10)


        self.botonOFF=tk.Button(self.frameOperacion, text='Apagar', font=('Arial',12,'bold'), width=12, bg='red',fg='white', command=self.apagarRadar ,state='disabled')
        self.botonOFF.grid(row=2, column=0, padx=10,pady=10)
        self.botonStandby=tk.Button(self.frameOperacion, text='Standby', font=('Arial',12,'bold'), width=12, bg='blue',fg='white', command=self.modoStandby ,state='disabled')
        self.botonStandby.grid(row=1,column=1,padx=10,pady=10)
        self.botonTEST=tk.Button(self.frameOperacion, text='TEST', font=('Arial',12,'bold'), width=12, bg='orange',fg='white', command=self.modoTEST, state='disabled')
        self.botonTEST.grid(row=2,column=1,padx=10,pady=10)
        self.botonON=tk.Button(self.frameOperacion, text='ON', font=('Arial',12,'bold'), width=12, bg='green2',fg='white', command=self.modoON, state='disabled')
        self.botonON.grid(row=3,column=1,padx=10,pady=10)
        
        self.frameSliders=ttk.Frame(self.frameControles, style='Frame1.TFrame', width=200, height=300)
        self.frameSliders.grid(row=0,column=1, padx=10,pady=10)


        self.LabelInclinacion=tk.Label(self.frameSliders, text='Inclinación', bg='black', fg='white', font=('Arial',12,'bold'))
        self.LabelInclinacion.grid(row=0,column=0, padx=10, pady=10)
        
        self.sliderInclinacion=ttk.Scale(self.frameSliders, state='disabled', to=15, from_ =-15, orient='horizontal', length=200, style='TScale', value=0)
        self.sliderInclinacion.grid(row=1, column=0, padx=10, pady=10)
        self.sliderInclinacion.bind("<B1-Motion>", self.actualizar_inclinacion)

        self.entryInclinacion=ttk.Entry(self.frameSliders, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entryInclinacion.grid(row=2,column=0,padx=10,pady=10)


        self.LabelGain=tk.Label(self.frameSliders, text='Ganancia', bg='black', fg='white', font=('Arial',12,'bold'))
        self.LabelGain.grid(row=0,column=1, padx=10, pady=10)
        
        self.sliderGain=ttk.Scale(self.frameSliders, state='disabled', to=0, from_ =-31.5, orient='horizontal', length=200, style='TScale', value=0)
        self.sliderGain.grid(row=1, column=1, padx=10, pady=10)
        self.sliderGain.bind("<ButtonRelease-1>", self.actualizar_gain)
        self.sliderGain.bind("<B1-Motion>", self.proximo_gain)


        self.entryGain=ttk.Entry(self.frameSliders, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entryGain.grid(row=2,column=1,padx=10,pady=10)


        self.frameBotones=ttk.Frame(self.frameControles, style='Frame1.TFrame', width=200, height=300)
        self.frameBotones.grid(row=0,column=2, padx=10,pady=10)

        self.botonRNGarriba=tk.Button(self.frameBotones, text='RNG ▲', font=('Arial',12,'bold'), width=12, bg='yellow',fg='white', command=self.rangoArriba ,state='disabled')
        self.botonRNGarriba.grid(row=2, column=1, padx=10,pady=10)
        
        self.botonRNGabajo=tk.Button(self.frameBotones, text='RNG ▼', font=('Arial',12,'bold'), width=12, bg='yellow',fg='white', command=self.rangoAbajo ,state='disabled')
        self.botonRNGabajo.grid(row=3, column=1, padx=10,pady=10)

        self.botonVp=tk.Button(self.frameBotones, text='VP', font=('Arial',12,'bold'), width=12, bg='red',fg='white', command=self.perfilVertical ,state='disabled')
        self.botonVp.grid(row=4, column=1, columnspan=4, padx=10,pady=10)

        self.botonTRKizquierda=tk.Button(self.frameBotones, text='TRK ◄', font=('Arial',12,'bold'), width=12, bg='blue',fg='white', command=self.trakerIzquierda ,state='disabled')
        self.botonTRKizquierda.grid(row=2, column=3, padx=10,pady=10)

        self.botonTRKderecha=tk.Button(self.frameBotones, text='TRK ►', font=('Arial',12,'bold'), width=12, bg='blue',fg='white', command=self.trakerDerecha ,state='disabled')
        self.botonTRKderecha.grid(row=3, column=3, padx=10,pady=10)
        
        self.entryTrack=ttk.Entry(self.frameBotones, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entryTrack.grid(row=2,column=4, rowspan=2,padx=10,pady=10)

        self.entryRNG=ttk.Entry(self.frameBotones, width=5,font=('Arial',12,'bold'),state='disabled')
        self.entryRNG.grid(row=2,column=0, rowspan=2,padx=10,pady=10)

        self.anguloTrack=0
        self.rango=80
        self.perfil=0


        self.flag=0
        self.flagsliders1=0
        self.flagsliders2=0

############################################################################3
    def modoStandby(self):
        self.botonOFF.config(state='normal')
        self.botonStandby.config(state='disabled')
        self.botonTEST.config(state='normal')
        self.botonON.config(state='disabled')
        self.labelEncendido.config(fg='blue',text='Standby')
        self.bt_desconectar.config(state='disabled')
        
        
        self.sliderInclinacion.set(0)
        self.sliderGain.set(0)

        self.entryInclinacion.config(state='enabled')
        self.entryGain.config(state='enabled')
        
        self.entryInclinacion.delete(0, tk.END)
        self.entryGain.delete(0, tk.END)
        self.entryInclinacion.insert(0,'0')
        self.entryGain.insert(0,'0')
        
        self.entryInclinacion.config(state='readonly')
        self.entryGain.config(foreground='gray')
        self.entryGain.config(state='readonly')


        self.sliderInclinacion.config(state='disabled')
        self.sliderGain.config(state='disabled')
        
        self.entryInclinacion.config(state='disabled')
        self.entryGain.config(state='disabled')

        self.botonRNGabajo.config(state='disabled')
        self.botonRNGarriba.config(state='disabled')
        self.botonVp.config(state='disabled')

        self.entryRNG.config(state='disabled')
        
        self.flag=0
        self.flagsliders1=0

        self.datos_arduino.enviar_datos("sby")
        
        


    def modoTEST(self):
        self.botonOFF.config(state='disabled')
        self.botonStandby.config(state='normal')
        self.botonTEST.config(state='disabled')
        self.botonON.config(state='normal')
        self.labelEncendido.config(fg='orange',text='TEST')
        self.sliderInclinacion.config(state='enabled')
        self.sliderGain.config(state='enabled')
        self.entryInclinacion.config(state='enabled')
        self.entryGain.config(state='enabled')
        self.botonTRKderecha.config(state='disabled')
        self.botonTRKizquierda.config(state='disabled')

        self.entryTrack.config(state='disabled')
       
        if self.flag==0:
            self.entryGain.delete(0, tk.END)
            self.entryInclinacion.delete(0, tk.END)
            self.entryInclinacion.insert(0,'0')
            self.entryGain.insert(0,'0')
            self.entryGain.config(foreground='black')
            self.entryInclinacion.config(state='readonly')
            self.entryGain.config(state='readonly')
            self.sliderGain.set(0)
            self.sliderInclinacion.set(0)
            self.botonRNGabajo.config(state='normal')
            self.botonRNGarriba.config(state='normal')
            self.botonVp.config(state='normal')

            self.entryRNG.config(state='enabled')
            self.entryRNG.delete(0, tk.END)
            self.entryRNG.insert(0,str(self.rango))
            self.entryRNG.config(state='readonly')

            self.flag=1
            self.flagsliders1=1

        self.datos_arduino.enviar_datos("tst")

    def modoON(self):
        self.botonOFF.config(state='disabled')
        self.botonStandby.config(state='disabled')
        self.botonTEST.config(state='normal')
        self.botonON.config(state='disabled')
        self.labelEncendido.config(fg='green',text='ON')

        self.botonTRKderecha.config(state='normal')
        self.botonTRKizquierda.config(state='normal')

        self.entryTrack.config(state='enabled')
        self.entryTrack.delete(0, tk.END)
        self.entryTrack.insert(0, str(self.anguloTrack))
        self.entryTrack.config(state='readonly')

        self.datos_arduino.enviar_datos("on")
        

    def apagarRadar(self):
        self.botonOFF.config(state='disabled')
        self.botonStandby.config(state='normal')
        self.botonTEST.config(state='disabled')
        self.botonON.config(state='disabled')
        self.labelEncendido.config(fg='red',text='OFF')
        self.bt_desconectar.config(state='normal')
        self.datos_arduino.enviar_datos("off")
 


    def proximo_gain(self,event):
        if self.flagsliders1==1:
            dato=self.sliderGain.get()
            dato = round(dato * 2) / 2
            self.sliderGain.set(dato)
            self.entryGain.config(state='enabled')
            self.entryGain.config(foreground='red')
            self.entryGain.delete(0, tk.END)
            self.entryGain.insert(0, dato)
            self.entryGain.config(state='readonly')

    def actualizar_gain(self,event):
        if self.flagsliders1==1:
            dato=self.sliderGain.get()
            dato = round(dato * 2) / 2
            self.sliderGain.set(dato)
            self.entryGain.config(state='enabled')
            self.entryGain.config(foreground='black')
            self.entryGain.delete(0, tk.END)
            self.entryGain.insert(0, dato)
            self.entryGain.config(state='readonly')

            self.datos_arduino.enviar_datos("G"+str(int(dato)))



    def actualizar_inclinacion(self,event):
        if self.flagsliders1==1:
            dato=self.sliderInclinacion.get()
            dato = round(dato * 4) / 4
            self.sliderInclinacion.set(dato)
            self.entryInclinacion.config(state='enabled')
            self.entryInclinacion.delete(0, tk.END)
            self.entryInclinacion.insert(0, dato)
            self.entryInclinacion.config(state='readonly')

            if dato<=0:
                self.datos_arduino.enviar_datos("TU"+str(dato))
            else:
                self.datos_arduino.enviar_datos("TD"+str(-dato))
            


    def rangoArriba(self):
        if self.rango<160:
            self.rango=self.rango*2
            
        elif self.rango==160:
            self.rango=240
        
        self.entryRNG.config(state='enabled')
        self.entryRNG.delete(0, tk.END)
        self.entryRNG.insert(0,str(int(self.rango)))
        self.entryRNG.config(state='readonly')
        if self.rango<=240:
            self.datos_arduino.enviar_datos("rng_arriba")



    def rangoAbajo(self):
        if self.rango<240 and self.rango>10:
            self.rango=self.rango/2
            
        elif self.rango==240:
            self.rango=160
        
        self.entryRNG.config(state='enabled')
        self.entryRNG.delete(0, tk.END)
        self.entryRNG.insert(0,str(int(self.rango)))
        self.entryRNG.config(state='readonly')
        if  self.rango>=10:
            self.datos_arduino.enviar_datos("rng_abajo")

        


    def perfilVertical(self):
        if(self.perfil==0):
            self.perfil=1
            self.botonVp.config(bg='green2')

        else:
            self.perfil=0
            self.botonVp.config(bg='red')

        self.datos_arduino.enviar_datos("vp")


    def trakerIzquierda(self):
        if self.anguloTrack>-45:
            self.anguloTrack=self.anguloTrack-1
            self.entryTrack.config(state='enabled')
            self.entryTrack.delete(0, tk.END)
            self.entryTrack.insert(0, str(self.anguloTrack))
            self.entryTrack.config(state='readonly')
            self.datos_arduino.enviar_datos("trk_izquierda")


    def trakerDerecha(self):
        if self.anguloTrack<45:
            self.anguloTrack=self.anguloTrack+1
            self.entryTrack.config(state='enabled')
            self.entryTrack.delete(0, tk.END)
            self.entryTrack.insert(0, str(self.anguloTrack))
            self.entryTrack.config(state='readonly')
            self.datos_arduino.enviar_datos("trk_derecha")



#########################################################################################3



    def actualizar_valor(self, event):
        if self.flagsliders2==1:
            dato1=str(int(self.slider1.get()))
            dato2=str(int(self.slider2.get()))
            self.entry1.config(state='enabled')
            self.entry1.config(foreground='red')
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, dato1)
            self.entry1.config(state='readonly')
            
            self.entry2.config(state='enabled')
            self.entry2.config(foreground='red')
            self.entry2.delete(0, tk.END)
            self.entry2.insert(0, dato2)
            self.entry2.config(state='readonly')
    

    def on_scale_release(self, event):
        if self.flagsliders2==1:
            dato1num = int(float(self.slider1.get()))
            dato2num = int(float(self.slider2.get()))
            dato1 = str(dato1num)
            dato2 = str(dato2num)
            
            self.entry1.config(state='enabled')
            self.entry1.delete(0, tk.END)
            self.entry1.config(foreground='black')
            self.entry1.insert(0, dato1)
            self.entry1.config(state='readonly')
            
            self.entry2.config(state='enabled')
            self.entry2.delete(0, tk.END)
            self.entry2.config(foreground='black')
            self.entry2.insert(0, dato2)
            self.entry2.config(state='readonly')
            
            self.datos_arduino.enviar_datos("M" + str(dato2) + "," + str(dato1))
            
            #manager=plt.new_figure_manager(self.fig.canvas)
            # Recrear la figura y el canvas
            
            elev=self.ax.elev
            azim=self.ax.azim
            plt.close(self.fig)  # Cerrar la figura anterior para liberar memoria
            #self.fig.clear()
            self.robot.plot([np.deg2rad(dato1num), np.deg2rad(dato2num)], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])

            self.fig=plt.gcf()
            self.ax=plt.gca()

            # Destruir el canvas anterior si existe
            #if hasattr(self.frameGG, 'canvas'):
            #    self.frameGG.canvas.get_tk_widget().destroy()

            
            #Crear un nuevo canvas y agregarlo al frame
            self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
            self.ax.plot([0,1],[0,0],[0,0])
            self.ax.view_init(elev=elev,azim=azim)
            self.frameGG.canvas.get_tk_widget().config(width=400,height=400)
            self.frameGG.canvas.draw()
            self.frameGG.canvas.get_tk_widget().grid(row=0,column=0)


    def actualizar_puertos(self):
        self.combobox_port.config(state='normal')
        self.datos_arduino.puertos_disponibles()
        self.port=self.datos_arduino.puertos
        self.combobox_port.config(values=self.port)
        self.combobox_port.current(0)
        self.combobox_port.config(state='readonly')

    def conectar_serial(self):
        self.slider1.config(state='enabled')
        self.entry1.config(state='enabled')
        self.bt_actualizar.config(state='disabled')
        self.bt_conectar.config(state='disabled')
        self.bt_desconectar.config(state='normal')
        self.slider2.config(state='enabled')
        self.entry2.config(state='enabled')
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)


        self.entry1.insert(0,'0')
        self.entry2.insert(0,'0')
        self.entry1.config(state='readonly')
        self.entry2.config(state='readonly')

        

        self.botonStandby.config(state='normal')



        self.datos_arduino.arduino.port = self.combobox_port.get()
        self.datos_arduino.arduino.baudrate =self.combobox_baud.get()
        self.datos_arduino.conexion_serial()
        self.flagsliders2=1
        messagebox.showinfo("Conexión","Conectado al puerto serial, control habilitado.")

    def desconectar_serial(self):

        self.entry1.config(state='enabled')
        self.entry1.delete(0, tk.END)
        self.entry1.insert(0, '0')
        self.entry1.config(state='readonly')
        
        self.entry2.config(state='enabled')
        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, '0')
        self.entry2.config(state='readonly')
        
        self.slider1.set(0)
        self.slider2.set(0)


        self.slider1.config(state='disabled')
        self.entry1.config(state='disabled')

        self.slider2.config(state='disabled')
        self.entry2.config(state='disabled')


        self.bt_actualizar.config(state='normal')
        self.bt_conectar.config(state='normal')
        self.bt_desconectar.config(state='disabled')

        self.botonStandby.config(state='disabled')

        self.datos_arduino.enviar_datos("0,0")
        self.datos_arduino.desconectar()

        plt.close(self.fig)  # Cerrar la figura anterior para liberar memoria
        #self.fig.clear()
        self.robot.plot([0, 0], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])

        self.fig=plt.gcf()
        self.ax=plt.gca()

        #Crear un nuevo canvas y agregarlo al frame
        self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
        self.ax.plot([0,1],[0,0],[0,0])
        self.frameGG.canvas.get_tk_widget().config(width=400,height=400)
        self.frameGG.canvas.draw()
        self.frameGG.canvas.get_tk_widget().grid(row=0,column=0)
        self.flagsliders2=0
        messagebox.showinfo("Desconexión","Retornando a posición HOME y desconectando serial.")


    def iniciar(self):
        self.root.mainloop()



if __name__== "__main__":
    app=aplicacion()
    app.iniciar()