"""
Panel de Visualización Responsivo para el Software Radar.

Este panel se adapta automáticamente al tamaño del contenedor.
"""
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import logging

logger = logging.getLogger(__name__)


class ResponsiveVisualizationPanel:
    """Panel de visualización responsivo con gráfico radar e indicadores."""
    
    def __init__(self, root, contenedor, serial):
        """
        Inicializa el panel de visualización responsivo.
        
        Args:
            root: Ventana principal
            contenedor: Frame contenedor
            serial: Objeto de comunicación serial
        """
        self.root = root
        self.contenedor = contenedor
        self.serial = serial
        
        # Importar módulos necesarios
        try:
            from mejorada import grafico, barrido
            import Interpretacion as intp
            
            self.grafico_class = grafico
            self.barrido_class = barrido
            self.intp = intp
        except ImportError as e:
            logger.error(f"Error al importar módulos legacy: {e}")
            raise
        
        # Frame principal RESPONSIVO
        self.principal = ctk.CTkFrame(self.contenedor, fg_color="#242424")
        # NOTA: NO hacemos grid aquí, se hace desde app_responsive.py
        
        # Configurar grid para responsividad
        self.principal.grid_rowconfigure(0, weight=1)
        self.principal.grid_columnconfigure(0, weight=0, minsize=280)  # Indicadores (ancho fijo mínimo)
        self.principal.grid_columnconfigure(1, weight=1)  # Gráfico (ocupa el resto del espacio)
        
        # ========== PANEL IZQUIERDO: INDICADORES ==========
        self._create_indicators_panel()
        
        # ========== PANEL DERECHO: GRÁFICO ==========
        self._create_graph_panel()
        
        # Inicializar variables
        self.barrido_actual = None
        self.barrido_nuevo = self.barrido_class(self.intp.main())
        self.lock = threading.Lock()
        
        self.gps1 = None
        self.gps2 = None
        self.compass = None
        
        # Variables de control de actualización
        self._update_id = None  # ID del timer de actualización
        self._update_running = False  # Flag para controlar el ciclo
    
    def _create_indicators_panel(self):
        """Crea el panel izquierdo con todos los indicadores."""
        # CORRECCIÓN: Sin ancho fijo para evitar sobreposición
        self.frameIndicadores = ctk.CTkScrollableFrame(self.principal)
        self.frameIndicadores.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Configurar grid interno
        self.frameIndicadores.grid_columnconfigure(0, weight=1)
        self.frameIndicadores.grid_columnconfigure(1, weight=2)
        
        # ========== TÍTULO ==========
        title = ctk.CTkLabel(
            self.frameIndicadores,
            text="📊 Indicadores",
            font=('Arial', 18, 'bold'),
            text_color="#3b82f6"
        )
        title.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")
        
        # ========== ACEPTACIÓN ==========
        self.l_aceptacion = ctk.CTkLabel(
            self.frameIndicadores,
            text="● Aceptación",
            text_color="red",
            font=('Arial', 14, 'bold')
        )
        self.l_aceptacion.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Separador
        separator1 = ctk.CTkFrame(self.frameIndicadores, height=2, fg_color="gray30")
        separator1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # ========== MODO DE OPERACIÓN ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Operación:",
            font=('Arial', 13, 'bold')
        ).grid(row=3, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.l_STDBY = ctk.CTkLabel(
            self.frameIndicadores,
            text="⏸ STDBY",
            font=('Arial', 12)
        )
        self.l_STDBY.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        
        self.l_TEST = ctk.CTkLabel(
            self.frameIndicadores,
            text="⚠ TEST",
            font=('Arial', 12)
        )
        self.l_TEST.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        
        self.l_ON = ctk.CTkLabel(
            self.frameIndicadores,
            text="✓ ON",
            font=('Arial', 12)
        )
        self.l_ON.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        
        # Separador
        separator2 = ctk.CTkFrame(self.frameIndicadores, height=2, fg_color="gray30")
        separator2.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # ========== FALLOS ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="⚠ Fallos",
            font=('Arial', 13, 'bold')
        ).grid(row=8, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.campoFallos = ctk.CTkTextbox(
            self.frameIndicadores,
            font=('Arial', 11),
            height=80,
            wrap="word"
        )
        self.campoFallos.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.campoFallos.insert("0.0", "Sin fallos reportados")
        self.campoFallos.configure(state="disabled")
        
        # ========== MODO ESPECIAL ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🔧 Modo especial",
            font=('Arial', 13, 'bold')
        ).grid(row=10, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.campoAnuncio = ctk.CTkTextbox(
            self.frameIndicadores,
            font=('Arial', 11),
            height=80,
            wrap="word"
        )
        self.campoAnuncio.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.campoAnuncio.insert("0.0", "Modo normal")
        self.campoAnuncio.configure(state="disabled")
        
        # Separador
        separator3 = ctk.CTkFrame(self.frameIndicadores, height=2, fg_color="gray30")
        separator3.grid(row=12, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # ========== PARÁMETROS ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="📏 Parámetros",
            font=('Arial', 15, 'bold'),
            text_color="#3b82f6"
        ).grid(row=13, column=0, columnspan=2, pady=(10, 15))
        
        # Rango
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Rango:",
            font=('Arial', 12, 'bold')
        ).grid(row=14, column=0, padx=10, pady=8, sticky="w")
        
        self.campoRango = ctk.CTkEntry(
            self.frameIndicadores,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        self.campoRango.grid(row=14, column=1, padx=10, pady=8, sticky="ew")
        self.campoRango.insert(0, "80 km")
        self.campoRango.configure(state="readonly")
        
        # Ganancia
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Ganancia:",
            font=('Arial', 12, 'bold')
        ).grid(row=15, column=0, padx=10, pady=8, sticky="w")
        
        self.campoGain = ctk.CTkEntry(
            self.frameIndicadores,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        self.campoGain.grid(row=15, column=1, padx=10, pady=8, sticky="ew")
        self.campoGain.insert(0, "0 dB")
        self.campoGain.configure(state="readonly")
        
        # Perfil Vertical
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Perfil V.:",
            font=('Arial', 12, 'bold')
        ).grid(row=16, column=0, padx=10, pady=8, sticky="w")
        
        self.campoVp = ctk.CTkEntry(
            self.frameIndicadores,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        self.campoVp.grid(row=16, column=1, padx=10, pady=8, sticky="ew")
        self.campoVp.insert(0, "OFF")
        self.campoVp.configure(state="readonly")
        
        # Inclinación
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Inclinación:",
            font=('Arial', 12, 'bold')
        ).grid(row=17, column=0, padx=10, pady=8, sticky="w")
        
        self.campoInclinacion = ctk.CTkEntry(
            self.frameIndicadores,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        self.campoInclinacion.grid(row=17, column=1, padx=10, pady=8, sticky="ew")
        self.campoInclinacion.insert(0, "0°")
        self.campoInclinacion.configure(state="readonly")
        
        # Track
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Track:",
            font=('Arial', 12, 'bold')
        ).grid(row=18, column=0, padx=10, pady=8, sticky="w")
        
        self.campoTrack = ctk.CTkEntry(
            self.frameIndicadores,
            font=('Arial', 12, 'bold'),
            justify='center'
        )
        self.campoTrack.grid(row=18, column=1, padx=10, pady=8, sticky="ew")
        self.campoTrack.insert(0, "0°")
        self.campoTrack.configure(state="readonly")
        
        # Separador
        separator4 = ctk.CTkFrame(self.frameIndicadores, height=2, fg_color="gray30")
        separator4.grid(row=19, column=0, columnspan=2, sticky="ew", padx=10, pady=15)
        
        # ========== SENSORES METEOROLÓGICOS ==========
        self._create_weather_sensors()
    
    def _create_weather_sensors(self):
        """Crea la sección de sensores meteorológicos."""
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🌤 Sensores Meteorológicos",
            font=('Arial', 15, 'bold'),
            text_color="#3b82f6"
        ).grid(row=20, column=0, columnspan=2, pady=(10, 15))
        
        # Frame para sensores
        self.frameSensor = ctk.CTkFrame(self.frameIndicadores, fg_color="#1a1a1a")
        self.frameSensor.grid(row=21, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Configurar grid
        self.frameSensor.grid_columnconfigure(0, weight=1)
        self.frameSensor.grid_columnconfigure(1, weight=1)
        
        # Temperatura
        ctk.CTkLabel(
            self.frameSensor,
            text="🌡 Temp:",
            font=('Arial', 11, 'bold')
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        
        self.campoTemperatura = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoTemperatura.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.campoTemperatura.insert(0, "-- °C")
        self.campoTemperatura.configure(state="readonly")
        
        # Humedad
        ctk.CTkLabel(
            self.frameSensor,
            text="💧 Humid:",
            font=('Arial', 11, 'bold')
        ).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        
        self.campoHumedad = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoHumedad.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        self.campoHumedad.insert(0, "-- %")
        self.campoHumedad.configure(state="readonly")
        
        # Presión
        ctk.CTkLabel(
            self.frameSensor,
            text="📊 Presión:",
            font=('Arial', 11, 'bold')
        ).grid(row=2, column=0, padx=10, pady=8, sticky="w")
        
        self.campoPresion = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoPresion.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.campoPresion.insert(0, "-- hPa")
        self.campoPresion.configure(state="readonly")
        
        # Viento
        ctk.CTkLabel(
            self.frameSensor,
            text="🌬 Viento:",
            font=('Arial', 11, 'bold')
        ).grid(row=3, column=0, padx=10, pady=8, sticky="w")
        
        self.campoViento = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoViento.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.campoViento.insert(0, "-- m/s")
        self.campoViento.configure(state="readonly")
        
        # Dirección del Viento
        ctk.CTkLabel(
            self.frameSensor,
            text="🧭 Dir. V.:",
            font=('Arial', 11, 'bold')
        ).grid(row=4, column=0, padx=10, pady=8, sticky="w")
        
        self.campoDireccionViento = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoDireccionViento.grid(row=4, column=1, padx=10, pady=8, sticky="ew")
        self.campoDireccionViento.insert(0, "-- °")
        self.campoDireccionViento.configure(state="readonly")
        
        # Precipitación
        ctk.CTkLabel(
            self.frameSensor,
            text="🌧 Precip:",
            font=('Arial', 11, 'bold')
        ).grid(row=5, column=0, padx=10, pady=8, sticky="w")
        
        self.campoPrecipitacion = ctk.CTkEntry(
            self.frameSensor,
            font=('Arial', 11),
            justify='center',
            width=80
        )
        self.campoPrecipitacion.grid(row=5, column=1, padx=10, pady=8, sticky="ew")
        self.campoPrecipitacion.insert(0, "-- mm")
        self.campoPrecipitacion.configure(state="readonly")
        
        # Separador
        separator5 = ctk.CTkFrame(self.frameIndicadores, height=2, fg_color="gray30")
        separator5.grid(row=22, column=0, columnspan=2, sticky="ew", padx=10, pady=15)
        
        # ========== GPS Y BRÚJULA ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🧭 GPS & Brújula",
            font=('Arial', 15, 'bold'),
            text_color="#3b82f6"
        ).grid(row=23, column=0, columnspan=2, pady=(10, 15))
        
        # Coordenadas GPS
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Coordenadas:",
            font=('Arial', 11, 'bold')
        ).grid(row=24, column=0, padx=10, pady=8, sticky="w")
        
        self.labelCoordenadas2 = ctk.CTkLabel(
            self.frameIndicadores,
            text="0.0, 0.0",
            font=('Arial', 11),
            text_color="lightblue"
        )
        self.labelCoordenadas2.grid(row=24, column=1, padx=10, pady=8, sticky="ew")
        
        # Dirección de brújula
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Dirección:",
            font=('Arial', 11, 'bold')
        ).grid(row=25, column=0, padx=10, pady=8, sticky="w")
        
        self.labelDir2 = ctk.CTkLabel(
            self.frameIndicadores,
            text="0°",
            font=('Arial', 11),
            text_color="lightblue"
        )
        self.labelDir2.grid(row=25, column=1, padx=10, pady=8, sticky="ew")
        
        # Aliases para compatibilidad con código legacy
        self.campoGanancia = self.campoGain
        self.campoFecha = ctk.CTkEntry(self.frameSensor, font=('Arial', 11), justify='center', width=80)
        self.campoTemp = ctk.CTkEntry(self.frameSensor, font=('Arial', 11), justify='center', width=80)
        self.campoDir = ctk.CTkEntry(self.frameSensor, font=('Arial', 11), justify='center', width=80)
        self.campoRain = ctk.CTkEntry(self.frameSensor, font=('Arial', 11), justify='center', width=80)
    
    def _create_graph_panel(self):
        """Crea el panel derecho con el gráfico del radar."""
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(self.principal, fg_color="#1a1a1a")
        self.frame_grafico.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        # Configurar grid para que el canvas ocupe todo el espacio
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        
        # Inicializar el gráfico
        self.grafico = self.grafico_class()
        self.fig = self.grafico.fig
        self.ax = self.grafico.ax
        
        # Canvas para el gráfico (RESPONSIVO)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Configurar el canvas para que se redimensione con la ventana
        self.canvas.get_tk_widget().bind("<Configure>", self._on_canvas_resize)
        
        logger.info("Panel de visualización responsivo creado exitosamente")
    
    def _on_canvas_resize(self, event):
        """Callback cuando el canvas se redimensiona."""
        try:
            # Obtener las nuevas dimensiones en pulgadas
            width_inches = event.width / self.fig.dpi
            height_inches = event.height / self.fig.dpi
            
            # Solo actualizar si el cambio es significativo (más de 0.5 pulgadas)
            if abs(self.fig.get_figwidth() - width_inches) > 0.5 or \
               abs(self.fig.get_figheight() - height_inches) > 0.5:
                self.fig.set_size_inches(width_inches, height_inches, forward=True)
                self.canvas.draw_idle()
        except Exception as e:
            logger.debug(f"Error al redimensionar canvas: {e}")
    
    # ==================== MÉTODOS DE ACTUALIZACIÓN ====================
    
    def actualizar_indicadores(self, datos):
        """
        Actualiza los indicadores con nuevos datos.
        
        Args:
            datos: Diccionario con los datos a actualizar
        """
        try:
            if 'aceptacion' in datos:
                color = "lightgreen" if datos['aceptacion'] else "red"
                text = "● Aceptado" if datos['aceptacion'] else "● Sin Aceptación"
                self.l_aceptacion.configure(text=text, text_color=color)
            
            if 'modo' in datos:
                modo = datos['modo']
                self.l_STDBY.configure(text_color="blue" if modo == "STDBY" else "gray")
                self.l_TEST.configure(text_color="orange" if modo == "TEST" else "gray")
                self.l_ON.configure(text_color="green" if modo == "ON" else "gray")
            
            if 'fallos' in datos:
                self.campoFallos.configure(state="normal")
                self.campoFallos.delete("0.0", "end")
                self.campoFallos.insert("0.0", datos['fallos'])
                self.campoFallos.configure(state="disabled")
            
            if 'rango' in datos:
                self.campoRango.configure(state="normal")
                self.campoRango.delete(0, "end")
                self.campoRango.insert(0, f"{datos['rango']} km")
                self.campoRango.configure(state="readonly")
            
            if 'ganancia' in datos:
                self.campoGain.configure(state="normal")
                self.campoGain.delete(0, "end")
                self.campoGain.insert(0, f"{datos['ganancia']} dB")
                self.campoGain.configure(state="readonly")
            
        except Exception as e:
            logger.error(f"Error al actualizar indicadores: {e}")
    
    def actualizar_sensores(self, datos):
        """
        Actualiza los sensores meteorológicos con nuevos datos.
        
        Args:
            datos: Diccionario con los datos meteorológicos
        """
        try:
            if 'temperatura' in datos:
                self.campoTemperatura.configure(state="normal")
                self.campoTemperatura.delete(0, "end")
                self.campoTemperatura.insert(0, f"{datos['temperatura']:.1f} °C")
                self.campoTemperatura.configure(state="readonly")
            
            if 'humedad' in datos:
                self.campoHumedad.configure(state="normal")
                self.campoHumedad.delete(0, "end")
                self.campoHumedad.insert(0, f"{datos['humedad']:.1f} %")
                self.campoHumedad.configure(state="readonly")
            
            if 'presion' in datos:
                self.campoPresion.configure(state="normal")
                self.campoPresion.delete(0, "end")
                self.campoPresion.insert(0, f"{datos['presion']:.1f} hPa")
                self.campoPresion.configure(state="readonly")
            
            if 'viento' in datos:
                self.campoViento.configure(state="normal")
                self.campoViento.delete(0, "end")
                self.campoViento.insert(0, f"{datos['viento']:.1f} m/s")
                self.campoViento.configure(state="readonly")
            
            if 'direccion_viento' in datos:
                self.campoDireccionViento.configure(state="normal")
                self.campoDireccionViento.delete(0, "end")
                self.campoDireccionViento.insert(0, f"{datos['direccion_viento']:.0f}°")
                self.campoDireccionViento.configure(state="readonly")
            
            if 'precipitacion' in datos:
                self.campoPrecipitacion.configure(state="normal")
                self.campoPrecipitacion.delete(0, "end")
                self.campoPrecipitacion.insert(0, f"{datos['precipitacion']:.2f} mm")
                self.campoPrecipitacion.configure(state="readonly")
            
        except Exception as e:
            logger.error(f"Error al actualizar sensores: {e}")
    
    def actualizar_grafico(self):
        """Actualiza el gráfico del radar."""
        try:
            self.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Error al actualizar gráfico: {e}")
    
    # ==================== MÉTODOS DE ACTUALIZACIÓN AUTOMÁTICA ====================
    
    def iniciar(self):
        """Inicia el ciclo de actualización automática."""
        # CORRECCIÓN: Prevenir múltiples ciclos de actualización
        if self._update_running:
            logger.warning("Ciclo de actualización ya está corriendo")
            return
        
        logger.info("Iniciando ciclo de actualización del panel de visualización")
        self._update_running = True
        self._update_id = self.root.after(1000, self.actualizar)
    
    def actualizar(self):
        """Actualiza todos los componentes del panel con nueva información."""
        import time
        import GPS
        import CargaSensor as CS
        
        tinicial = time.time()
        
        try:
            # Actualizar barrido
            self.barrido_actual = self.barrido_nuevo
            hilo = threading.Thread(target=self.nueva_lectura, daemon=True)
            hilo.start()
            
            # Leer datos GPS y brújula
            self.serial.leer_datos()
            gps1 = self.serial.datos_recibidos.get()
            print(f"GPS1: {gps1}")
            
            self.serial.leer_datos()
            gps2 = self.serial.datos_recibidos.get()
            print(f"GPS2: {gps2}")
            
            self.serial.leer_datos()
            self.compass = self.serial.datos_recibidos.get()
            print(f"Compass: {self.compass}")
            
            self.gps1 = GPS.main(gps1)
            self.gps2 = GPS.main(gps2)
            
            self.serial.arduino.reset_input_buffer()
            
            # Procesar coordenadas GPS
            if (self.gps1.get("fix_quality") == 0 or 
                self.gps1.get("satellites_in_use") < 4 or 
                self.gps2.get("status") == 'V'):
                self.latitud = 0
                self.longitud = 0
            else:
                self.latitud = float(self.gps1.get("latitude"))
                self.longitud = float(self.gps1.get("longitude"))
            
            # Actualizar labels de GPS
            self.labelCoordenadas2.configure(
                text=f"{round(self.latitud, 5)}, {round(self.longitud, 5)}"
            )
            self.labelDir2.configure(text=str(self.compass))
            
            # Actualizar gráfico del radar
            self.grafico.actualizar_grafico(
                self.barrido_actual,
                self.latitud,
                self.longitud,
                self.compass
            )
            self.canvas.draw_idle()
            
            # Guardar imágenes (opcional, comentado por rendimiento)
            # self.grafico.fig.savefig('radar.png', transparent=True)
            
            # Actualizar indicador de aceptación
            if self.barrido_actual.aceptacion == 1:
                self.l_aceptacion.configure(
                    text="● Aceptado",
                    text_color="lightgreen"
                )
            else:
                self.l_aceptacion.configure(
                    text="● Sin Aceptación",
                    text_color="red"
                )
            
            # Actualizar modo de operación
            self.l_STDBY.configure(text_color="gray")
            self.l_ON.configure(text_color="gray")
            self.l_TEST.configure(text_color="gray")
            
            if self.barrido_actual.operacion == 0:
                self.l_STDBY.configure(text_color="blue")
            elif self.barrido_actual.operacion == 1:
                self.l_ON.configure(text_color="lightgreen")
            elif self.barrido_actual.operacion == 4:
                self.l_TEST.configure(text_color="orange")
            
            # Actualizar fallos
            self.campoFallos.configure(state="normal")
            self.campoFallos.delete("0.0", "end")
            if len(self.barrido_actual.fallos) != 0:
                for fallo_id in self.barrido_actual.fallos:
                    if fallo_id == 5:
                        self.campoFallos.insert("end", "⚠ Antena\n")
                    elif fallo_id == 6:
                        self.campoFallos.insert("end", "⚠ Transmisión\n")
            else:
                self.campoFallos.insert("end", "✓ Sin fallos")
            self.campoFallos.configure(state="disabled")
            
            # Actualizar modo especial
            self.campoAnuncio.configure(state="normal")
            self.campoAnuncio.delete("0.0", "end")
            if len(self.barrido_actual.anuncio) != 0:
                if 7 in self.barrido_actual.anuncio:
                    self.campoAnuncio.insert("end", "📊 Perfil vertical\n")
                else:
                    for anuncio_id in self.barrido_actual.anuncio:
                        if anuncio_id == 0:
                            self.campoAnuncio.insert("end", "🌪 Turbulencia\n")
                        elif anuncio_id == 1:
                            self.campoAnuncio.insert("end", "☁ Clima\n")
                        elif anuncio_id == 2:
                            self.campoAnuncio.insert("end", "🔍 Filtración\n")
                        elif anuncio_id == 3:
                            self.campoAnuncio.insert("end", "◢ Sector reducido\n")
                        elif anuncio_id == 4:
                            self.campoAnuncio.insert("end", "📏 Fuera de rango\n")
            else:
                self.campoAnuncio.insert("end", "✓ Sin modos especiales")
            self.campoAnuncio.configure(state="disabled")
            
            # Actualizar parámetros del radar
            self.campoGanancia.configure(state="normal")
            self.campoGanancia.delete(0, "end")
            self.campoGanancia.insert(0, f"{self.barrido_actual.ganancia} dB")
            self.campoGanancia.configure(state="readonly")
            
            self.campoRango.configure(state="normal")
            self.campoRango.delete(0, "end")
            self.campoRango.insert(0, f"{self.barrido_actual.rango} km")
            self.campoRango.configure(state="readonly")
            
            self.campoInclinacion.configure(state="normal")
            self.campoInclinacion.delete(0, "end")
            self.campoInclinacion.insert(0, f"{self.barrido_actual.inclinacion}°")
            self.campoInclinacion.configure(state="readonly")
            
            # Actualizar sensores meteorológicos
            try:
                nombre_archivo = "CR310_RK900_10.csv"
                datosSensor = CS.obtener_ultima_lectura(nombre_archivo)
                
                if datosSensor:
                    # Temperatura
                    if 'Temperature' in datosSensor:
                        self.campoTemperatura.configure(state="normal")
                        self.campoTemperatura.delete(0, "end")
                        self.campoTemperatura.insert(0, f"{datosSensor.get('Temperature')} °C")
                        self.campoTemperatura.configure(state="readonly")
                    
                    # Dirección del viento
                    if 'Wind_Direction' in datosSensor:
                        self.campoDireccionViento.configure(state="normal")
                        self.campoDireccionViento.delete(0, "end")
                        self.campoDireccionViento.insert(0, f"{datosSensor.get('Wind_Direction')}°")
                        self.campoDireccionViento.configure(state="readonly")
                    
                    # Precipitación
                    if 'Precipitation' in datosSensor:
                        self.campoPrecipitacion.configure(state="normal")
                        self.campoPrecipitacion.delete(0, "end")
                        self.campoPrecipitacion.insert(0, f"{datosSensor.get('Precipitation')} mm")
                        self.campoPrecipitacion.configure(state="readonly")
            except Exception as e:
                logger.warning(f"No se pudieron cargar datos meteorológicos: {e}")
            
            # Calcular tiempo de ejecución
            tiempo_ejecucion = time.time() - tinicial
            logger.debug(f"Tiempo de actualización: {tiempo_ejecucion:.3f}s")
            
        except Exception as e:
            logger.error(f"Error durante actualización: {e}", exc_info=True)
        
        # Programar próxima actualización solo si el ciclo está activo
        if self._update_running:
            self._update_id = self.root.after(1000, self.actualizar)
    
    def detener(self):
        """Detiene el ciclo de actualización automática."""
        logger.info("Deteniendo ciclo de actualización del panel de visualización")
        self._update_running = False
        
        # Cancelar el timer pendiente si existe
        if self._update_id is not None:
            try:
                self.root.after_cancel(self._update_id)
                self._update_id = None
                logger.info("Timer de actualización cancelado exitosamente")
            except Exception as e:
                logger.warning(f"Error al cancelar timer: {e}")
    
    def nueva_lectura(self):
        """Lee nuevos datos en un hilo separado."""
        try:
            time.sleep(5)
            with self.lock:
                self.barrido_nuevo = self.barrido_class(self.intp.main())
        except Exception as e:
            logger.error(f"Error en nueva_lectura: {e}")


# Alias para compatibilidad
panel_visualizacion = ResponsiveVisualizationPanel

