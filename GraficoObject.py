import matplotlib.pyplot as plt
import numpy as np
import Interpretacion as intp
import Captura as cap
import time
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.fig, self.ax= plt.subplots(subplot_kw={'polar': True}, figsize=(3.0, 3.0))
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

    def actualizar_grafico(self, barrido_nuevo):
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
        
class aplicacion:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Interfaz de control del radar")
        self.root.config(bg="lightgray")
        self.s=ttk.Style()
        self.s.configure('Frame1.TFrame', background='lightgray')
        self.frame_grafico = ttk.Frame(self.root, style='Frame1.TFrame', width=600, height=600)
        
        self.grafico=grafico()
        self.fig=self.grafico.fig
        self.ax=self.grafico.ax

        self.frame_grafico.grid(row=0, column=1, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().config(width=400, height=400)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.frameIndicadores = ttk.Frame(self.root,style='Frame1.TFrame',width=200,height=400)
        self.frameIndicadores.grid(row=0,column=0,padx=10,pady=10)

        self.l_aceptacion=tk.Label(self.frameIndicadores,text="Aceptacion", bg='lightgray', fg='red', font=('Arial',12,'bold'))
        self.l_aceptacion.grid(row=0,column=0,padx=10,pady=10,columnspan=2)

        self.l_modo=tk.Label(self.frameIndicadores,text="Operacion:", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_modo.grid(row=1,column=0,padx=10,pady=10)

        self.l_STDBY=tk.Label(self.frameIndicadores,text="STDBY", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_STDBY.grid(row=1,column=1,padx=10,pady=10)

        self.l_TEST=tk.Label(self.frameIndicadores,text="TEST", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_TEST.grid(row=2,column=1,padx=10,pady=10)

        self.l_ON=tk.Label(self.frameIndicadores,text="ON", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_ON.grid(row=3,column=1,padx=10,pady=10)

        self.l_fallos=tk.Label(self.frameIndicadores,text="Fallos", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_fallos.grid(row=4,column=0,padx=10,pady=10)

        self.campoFallos=tk.Text(self.frameIndicadores,width=20,font=('Arial',12,'bold'),state="normal",height=2)
        self.campoFallos.grid(row=4,column=1,padx=10,pady=10)
        self.campoFallos.insert(tk.END,"iniciando")

        self.l_anuncio=tk.Label(self.frameIndicadores,text="Modo especial", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_anuncio.grid(row=5,column=0,padx=10,pady=10)

        self.campoAnuncio=tk.Text(self.frameIndicadores,width=20,font=('Arial',12,'bold'),state="normal",height=2)
        self.campoAnuncio.grid(row=5,column=1,padx=10,pady=10)
        self.campoAnuncio.insert(tk.END,"iniciando")

        self.l_rango=tk.Label(self.frameIndicadores,text="Rango:", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_rango.grid(row=6,column=0,padx=10,pady=10)

        self.campoRango=tk.Entry(self.frameIndicadores,width=20,font=('Arial',12,'bold'))
        self.campoRango.grid(row=6,column=1,padx=10,pady=10)
        self.campoRango.insert(0,"iniciando")

        self.l_ganancia=tk.Label(self.frameIndicadores,text="Ganancia:", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_ganancia.grid(row=7,column=0,padx=10,pady=10)

        self.campoGanancia=tk.Entry(self.frameIndicadores,width=20,font=('Arial',12,'bold'))
        self.campoGanancia.grid(row=7,column=1,padx=10,pady=10)
        self.campoGanancia.insert(0,"iniciando")

        self.l_inclinacion=tk.Label(self.frameIndicadores,text="Inclinacion:", bg='lightgray', fg='black', font=('Arial',12,'bold'))
        self.l_inclinacion.grid(row=8,column=0,padx=10,pady=10)

        self.campoInclinacion=tk.Entry(self.frameIndicadores,width=20,font=('Arial',12,'bold'))
        self.campoInclinacion.grid(row=8,column=1,padx=10,pady=10)
        self.campoInclinacion.insert(0,"iniciando")

        self.close_button = ttk.Button(self.root, text="Cerrar", command=self.root.quit)
        self.close_button.grid(row=2,column=0,columnspan=2)

        self.barrido_actual=None
        self.barrido_nuevo=barrido(intp.main())
        self.lock=threading.Lock()
    
    def iniciar(self):
        self.root.after(1000,self.actualizar)
        self.root.update_idletasks()
        self.root.mainloop()

    def actualizar(self):
        tinicial=time.time()

        self.barrido_actual=self.barrido_nuevo
        hilo=threading.Thread(target=self.nueva_lectura,daemon=True)
        hilo.start()
        self.grafico.actualizar_grafico(self.barrido_actual)
        self.canvas.draw_idle()
        self.root.update_idletasks()
        
        if self.barrido_actual.aceptacion==1:
            self.l_aceptacion.config(fg="green")

        if(self.barrido_actual.operacion==0):
            self.l_STDBY.config(fg='blue')
            self.l_ON.config(fg='black')
            self.l_TEST.config(fg='black')
        elif(self.barrido_actual.operacion==1):
            self.l_ON.config(fg='green')
            self.l_STDBY.config(fg='black')
            self.l_TEST.config(fg='black')
        elif(self.barrido_actual.operacion==4):
            self.l_TEST.config(fg='red')
            self.l_ON.config(fg='black')
            self.l_STDBY.config(fg='black')

        self.campoFallos.delete('1.0',tk.END)
        if len(self.barrido_actual.fallos)!=0:
            self.l_fallos.config(fg="red")
            for h in range(0,len(self.barrido_actual.fallos)):
                if self.barrido_actual.fallos[h]== 5:
                    self.campoFallos.insert(tk.END,"Antena \n")
                elif self.barrido_actual.fallos[h]== 6:
                    self.campoFallos.insert(tk.END,"Transmision \n")
        else:
            self.campoFallos.insert(tk.END, "Sin fallos")
            self.l_fallos.config(fg='black')

        self.campoAnuncio.delete('1.0',tk.END)
        if len(self.barrido_actual.anuncio)!=0:
            self.l_anuncio.config(fg="orange")

            if 7 in self.barrido_actual.anuncio:
                self.campoAnuncio.insert(tk.END,"Perfil vertical \n")
            else:    
                for f in range(0,len(self.barrido_actual.anuncio)):
                    if self.barrido_actual.anuncio[f]== 0:
                        self.campoAnuncio.insert(tk.END,"Turbulencia \n")
                    elif self.barrido_actual.anuncio[f]== 1:
                        self.campoAnuncio.insert(tk.END,"Clima \n")
                    elif self.barrido_actual.anuncio[f]== 2:
                        self.campoAnuncio.insert(tk.END,"Filtracion \n")
                    elif self.barrido_actual.anuncio[f]== 3:
                        self.campoAnuncio.insert(tk.END,"Sector reducido \n")
                    elif self.barrido_actual.anuncio[f]== 4:
                        self.campoAnuncio.insert(tk.END,"Fuera de rango \n")
        else:
            self.campoAnuncio.insert(tk.END,"Sin modos")
            self.l_anuncio.config(fg='black')

        self.campoGanancia.config(state='normal')
        self.campoGanancia.delete(0,tk.END)
        self.campoGanancia.insert(0,str(self.barrido_actual.ganancia)+ " dB")

        self.campoGanancia.config(state='readonly')

        self.campoRango.config(state='normal')
        self.campoRango.delete(0,tk.END)
        self.campoRango.insert(0,self.barrido_actual.rango)
        self.campoRango.config(state='readonly')

        self.campoInclinacion.config(state='normal')
        self.campoInclinacion.delete(0,tk.END)
        self.campoInclinacion.insert(0,str(self.barrido_actual.inclinacion)+"°")
        self.campoInclinacion.config(state='readonly')


        print(time.time()-tinicial)
        self.root.after(15000,self.actualizar)
    
    def nueva_lectura(self):
        cap.capturaDatos()
        with self.lock:
            self.barrido_nuevo=barrido(intp.main())



if __name__== "__main__":
    app=aplicacion()
    app.iniciar()
