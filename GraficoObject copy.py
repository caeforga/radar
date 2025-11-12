import matplotlib.pyplot as plt
import numpy as np
import Interpretacion as intp
import Captura as cap
import time
import threading
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("dark")  # Puedes cambiar a "light" o "system"
ctk.set_default_color_theme("blue")  # Temas disponibles: "blue", "green", "dark-blue"

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
        self.root = ctk.CTk()
        self.root.title("Interfaz de control del radar")
        
        # Configurar el grid para que sea responsivo
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(self.root)
        self.frame_grafico.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        
        # Frame para los indicadores
        self.frameIndicadores = ctk.CTkFrame(self.root, width=200)
        self.frameIndicadores.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Inicializar el gráfico
        self.grafico = grafico()
        self.fig = self.grafico.fig
        self.ax = self.grafico.ax

        # Canvas para el gráfico
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Configurar los widgets de los indicadores
        self._crear_widgets_indicadores()
        
        self.barrido_actual = None
        self.barrido_nuevo = barrido(intp.main())
        self.lock = threading.Lock()
    
    def _crear_widgets_indicadores(self):
        """Crea todos los widgets de los indicadores en el frame izquierdo"""
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
        
        # Botón de cerrar
        self.close_button = ctk.CTkButton(self.root, text="Cerrar", command=self.root.quit)
        self.close_button.grid(row=1, column=0, columnspan=2, pady=10)
    
    def iniciar(self):
        self.root.after(1000, self.actualizar)
        self.root.mainloop()

    def actualizar(self):
        tinicial = time.time()

        self.barrido_actual = self.barrido_nuevo
        hilo = threading.Thread(target=self.nueva_lectura, daemon=True)
        hilo.start()
        self.grafico.actualizar_grafico(self.barrido_actual)
        self.canvas.draw_idle()
        
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

        print(time.time() - tinicial)
        self.root.after(15000, self.actualizar)
    
    def nueva_lectura(self):
        ##cap.capturaDatos()
        time.sleep(5)
        with self.lock:
            self.barrido_nuevo = barrido(intp.main())

if __name__ == "__main__":
    app = aplicacion()
    app.iniciar()