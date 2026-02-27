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
import asyncio
import urllib.request
import json

logger = logging.getLogger(__name__)

try:
    import winsdk.windows.devices.geolocation as wdg
    WINSDK_DISPONIBLE = True
except ImportError:
    WINSDK_DISPONIBLE = False
    logger.info("winsdk no disponible, se usará geolocalización por IP como fallback")


def _obtener_ubicacion_winsdk():
    """
    Obtiene la ubicación usando Windows Location Service (GPS/Wi-Fi/Cell).
    Mucho más precisa que la geolocalización por IP.
    
    Returns:
        tuple: (latitud, longitud) o None si falla
    """
    async def _get_coords():
        locator = wdg.Geolocator()
        locator.desired_accuracy = wdg.PositionAccuracy.HIGH
        pos = await locator.get_geoposition_async()
        return (pos.coordinate.latitude, pos.coordinate.longitude)
    
    try:
        lat, lon = asyncio.run(_get_coords())
        if lat != 0 or lon != 0:
            logger.info(f"Ubicación obtenida via Windows Location Service: {lat}, {lon}")
            return float(lat), float(lon)
    except PermissionError:
        logger.warning("Permiso denegado: habilita el acceso a ubicación en Configuración de Windows")
    except Exception as e:
        logger.warning(f"Error con Windows Location Service: {e}")
    return None


def _obtener_ubicacion_ip():
    """
    Fallback: obtiene la ubicación por geolocalización de IP.
    Menos precisa (nivel ciudad), pero no requiere permisos especiales.
    
    Returns:
        tuple: (latitud, longitud) o None si falla
    """
    apis = [
        ("http://ip-api.com/json/", lambda d: (d.get("lat", 0), d.get("lon", 0))),
        ("https://ipapi.co/json/", lambda d: (d.get("latitude", 0), d.get("longitude", 0))),
        ("https://ipinfo.io/json", lambda d: tuple(map(float, d.get("loc", "0,0").split(",")))),
    ]
    
    for url, parser in apis:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                lat, lon = parser(data)
                if lat != 0 or lon != 0:
                    logger.info(f"Ubicación obtenida via IP ({url}): {lat}, {lon}")
                    return float(lat), float(lon)
        except Exception as e:
            logger.debug(f"Error con API {url}: {e}")
            continue
    return None


def obtener_ubicacion_pc():
    """
    Obtiene la ubicación del PC. Intenta primero con Windows Location Service
    (GPS/Wi-Fi, alta precisión) y si falla usa geolocalización por IP como fallback.
    
    Returns:
        tuple: (latitud, longitud) o (0, 0) si todos los métodos fallan
    """
    if WINSDK_DISPONIBLE:
        resultado = _obtener_ubicacion_winsdk()
        if resultado:
            return resultado
    
    resultado = _obtener_ubicacion_ip()
    if resultado:
        return resultado
    
    logger.warning("No se pudo obtener la ubicación del PC por ningún método")
    return 0, 0

# Import opcional de Captura (requiere saleae)
try:
    import Captura as cap
    CAPTURA_DISPONIBLE = True
except ImportError:
    cap = None
    CAPTURA_DISPONIBLE = False
    logger.warning("Módulo Captura no disponible (saleae no instalado)")


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
            self.cap = cap  # Puede ser None si saleae no está instalado
            self.captura_disponible = CAPTURA_DISPONIBLE
        except ImportError as e:
            logger.error(f"Error al importar módulos legacy: {e}")
            raise
        
        # Frame principal RESPONSIVO
        self.principal = ctk.CTkFrame(self.contenedor, fg_color="#242424")
        # NOTA: NO hacemos grid aquí, se hace desde app_responsive.py
        
        # Configurar grid para responsividad - Nuevo layout optimizado
        # Fila 0: Panel principal (indicadores + gráfico) - peso alto
        # Fila 1: Barra de parámetros inferior - altura fija
        self.principal.grid_rowconfigure(0, weight=1)
        self.principal.grid_rowconfigure(1, weight=0, minsize=66)  # Barra inferior compacta
        self.principal.grid_columnconfigure(0, weight=0, minsize=200)  # Indicadores compactos
        self.principal.grid_columnconfigure(1, weight=1)  # Gráfico (ocupa el resto)
        
        # ========== PANEL IZQUIERDO: INDICADORES COMPACTOS ==========
        self._create_indicators_panel()
        
        # ========== PANEL DERECHO: GRÁFICO ==========
        self._create_graph_panel()
        
        # ========== BARRA INFERIOR: PARÁMETROS CRÍTICOS ==========
        self._create_bottom_bar()
        
        # Inicializar variables
        self.barrido_actual = None
        self.barrido_nuevo = None
        self.lock = threading.Lock()
        
        # Intentar cargar datos iniciales del radar
        try:
            datos_iniciales = self.intp.main()
            if datos_iniciales:
                self.barrido_nuevo = self.barrido_class(datos_iniciales)
                logger.info("Datos iniciales del radar cargados correctamente")
        except FileNotFoundError as e:
            logger.warning(f"Archivo de lecturas no encontrado: {e}")
            logger.info("El panel funcionará sin datos iniciales (esperando conexión al radar)")
        except Exception as e:
            logger.warning(f"No se pudieron cargar datos iniciales: {e}")
            logger.info("El panel funcionará sin datos iniciales (esperando conexión al radar)")
        
        self.gps1 = None
        self.gps2 = None
        self.compass = 0
        
        # Variables para GPS del PC
        self.latitud = 0
        self.longitud = 0
        self._ubicacion_pc_obtenida = False
        self._ubicacion_lock = threading.Lock()
        
        # Obtener ubicación del PC al iniciar (en segundo plano)
        threading.Thread(target=self._obtener_ubicacion_pc, daemon=True).start()
        
        # Variables de control de actualización
        self._update_id = None  # ID del timer de actualización
        self._update_running = False  # Flag para controlar el ciclo
    
    def _obtener_ubicacion_pc(self):
        """Obtiene la ubicación del PC en segundo plano usando geolocalización por IP."""
        try:
            lat, lon = obtener_ubicacion_pc()
            if lat != 0 or lon != 0:
                with self._ubicacion_lock:
                    self.latitud = lat
                    self.longitud = lon
                    self._ubicacion_pc_obtenida = True
                logger.info(f"Ubicación del PC establecida: {lat}, {lon}")
        except Exception as e:
            logger.error(f"Error obteniendo ubicación del PC: {e}")
    
    def _create_indicators_panel(self):
        """Crea el panel izquierdo COMPACTO con indicadores de estado."""
        # Panel compacto sin scroll para indicadores esenciales
        self.frameIndicadores = ctk.CTkFrame(self.principal, fg_color="#1a1a1a")
        self.frameIndicadores.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Configurar grid interno
        self.frameIndicadores.grid_columnconfigure(0, weight=1)
        
        # ========== TÍTULO ==========
        title = ctk.CTkLabel(
            self.frameIndicadores,
            text="📊 Estado",
            font=('Arial', 16, 'bold'),
            text_color="#3b82f6"
        )
        title.grid(row=0, column=0, pady=(10, 10), sticky="ew")
        
        # ========== ACEPTACIÓN ==========
        self.l_aceptacion = ctk.CTkLabel(
            self.frameIndicadores,
            text="● Aceptación",
            text_color="red",
            font=('Arial', 13, 'bold')
        )
        self.l_aceptacion.grid(row=1, column=0, padx=10, pady=8)
        
        # Separador
        separator1 = ctk.CTkFrame(self.frameIndicadores, height=1, fg_color="gray40")
        separator1.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # ========== MODO DE OPERACIÓN (compacto horizontal) ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="Operación:",
            font=('Arial', 11, 'bold')
        ).grid(row=3, column=0, padx=10, pady=(5, 2), sticky="w")
        
        # Frame para modos en línea
        frame_modos = ctk.CTkFrame(self.frameIndicadores, fg_color="transparent")
        frame_modos.grid(row=4, column=0, padx=10, pady=2, sticky="ew")
        frame_modos.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.l_STDBY = ctk.CTkLabel(frame_modos, text="⏸ STDBY", font=('Arial', 10), text_color="gray")
        self.l_STDBY.grid(row=0, column=0, padx=2)
        
        self.l_TEST = ctk.CTkLabel(frame_modos, text="⚠ TEST", font=('Arial', 10), text_color="gray")
        self.l_TEST.grid(row=0, column=1, padx=2)
        
        self.l_ON = ctk.CTkLabel(frame_modos, text="✓ ON", font=('Arial', 10), text_color="gray")
        self.l_ON.grid(row=0, column=2, padx=2)
        
        # Separador
        separator2 = ctk.CTkFrame(self.frameIndicadores, height=1, fg_color="gray40")
        separator2.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        
        # ========== FALLOS ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="⚠ Fallos",
            font=('Arial', 11, 'bold')
        ).grid(row=6, column=0, padx=10, pady=(5, 2), sticky="w")
        
        self.campoFallos = ctk.CTkTextbox(
            self.frameIndicadores,
            font=('Arial', 10),
            height=50,
            wrap="word",
            fg_color="#2a2a2a"
        )
        self.campoFallos.grid(row=7, column=0, padx=10, pady=2, sticky="ew")
        self.campoFallos.insert("0.0", "Sin fallos")
        self.campoFallos.configure(state="disabled")
        
        # ========== MODO ESPECIAL ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🔧 Modo Especial",
            font=('Arial', 11, 'bold')
        ).grid(row=8, column=0, padx=10, pady=(5, 2), sticky="w")
        
        self.campoAnuncio = ctk.CTkTextbox(
            self.frameIndicadores,
            font=('Arial', 10),
            height=50,
            wrap="word",
            fg_color="#2a2a2a"
        )
        self.campoAnuncio.grid(row=9, column=0, padx=10, pady=2, sticky="ew")
        self.campoAnuncio.insert("0.0", "Normal")
        self.campoAnuncio.configure(state="disabled")
        
        # Separador
        separator3 = ctk.CTkFrame(self.frameIndicadores, height=1, fg_color="gray40")
        separator3.grid(row=10, column=0, sticky="ew", padx=10, pady=5)
        
        # ========== GPS & BRÚJULA (compacto) ==========
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🧭 GPS",
            font=('Arial', 11, 'bold')
        ).grid(row=11, column=0, padx=10, pady=(5, 2), sticky="w")
        
        self.labelCoordenadas2 = ctk.CTkLabel(
            self.frameIndicadores,
            text="0.0, 0.0",
            font=('Arial', 10),
            text_color="lightblue"
        )
        self.labelCoordenadas2.grid(row=12, column=0, padx=10, pady=2, sticky="ew")
        
        # Dirección
        frame_dir = ctk.CTkFrame(self.frameIndicadores, fg_color="transparent")
        frame_dir.grid(row=13, column=0, padx=10, pady=2, sticky="ew")
        
        ctk.CTkLabel(frame_dir, text="Dir:", font=('Arial', 10)).pack(side="left")
        self.labelDir2 = ctk.CTkLabel(frame_dir, text="0°", font=('Arial', 10), text_color="lightblue")
        self.labelDir2.pack(side="left", padx=5)
        
        # ========== SENSORES METEOROLÓGICOS (en panel expandible) ==========
        self._create_weather_sensors_compact()
    
    def _create_weather_sensors_compact(self):
        """Crea la sección de sensores meteorológicos compacta."""
        # Separador
        separator4 = ctk.CTkFrame(self.frameIndicadores, height=1, fg_color="gray40")
        separator4.grid(row=14, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.frameIndicadores,
            text="🌤 Meteorología",
            font=('Arial', 11, 'bold')
        ).grid(row=15, column=0, padx=10, pady=(5, 2), sticky="w")
        
        # Frame compacto para sensores
        self.frameSensor = ctk.CTkFrame(self.frameIndicadores, fg_color="#2a2a2a")
        self.frameSensor.grid(row=16, column=0, padx=10, pady=5, sticky="ew")
        self.frameSensor.grid_columnconfigure(1, weight=1)
        
        # Temperatura
        ctk.CTkLabel(self.frameSensor, text="🌡", font=('Arial', 9)).grid(row=0, column=0, padx=3, pady=2)
        self.campoTemperatura = ctk.CTkLabel(self.frameSensor, text="--°C", font=('Arial', 9), text_color="cyan")
        self.campoTemperatura.grid(row=0, column=1, padx=3, pady=2, sticky="w")
        
        # Humedad
        ctk.CTkLabel(self.frameSensor, text="💧", font=('Arial', 9)).grid(row=0, column=2, padx=3, pady=2)
        self.campoHumedad = ctk.CTkLabel(self.frameSensor, text="--%", font=('Arial', 9), text_color="cyan")
        self.campoHumedad.grid(row=0, column=3, padx=3, pady=2, sticky="w")
        
        # Viento
        ctk.CTkLabel(self.frameSensor, text="🌬", font=('Arial', 9)).grid(row=1, column=0, padx=3, pady=2)
        self.campoViento = ctk.CTkLabel(self.frameSensor, text="--m/s", font=('Arial', 9), text_color="cyan")
        self.campoViento.grid(row=1, column=1, padx=3, pady=2, sticky="w")
        
        # Precipitación
        ctk.CTkLabel(self.frameSensor, text="🌧", font=('Arial', 9)).grid(row=1, column=2, padx=3, pady=2)
        self.campoPrecipitacion = ctk.CTkLabel(self.frameSensor, text="--mm", font=('Arial', 9), text_color="cyan")
        self.campoPrecipitacion.grid(row=1, column=3, padx=3, pady=2, sticky="w")
        
        # Presión y dirección del viento (ocultos pero disponibles para compatibilidad)
        self.campoPresion = ctk.CTkLabel(self.frameSensor, text="--", font=('Arial', 9))
        self.campoDireccionViento = ctk.CTkLabel(self.frameSensor, text="--", font=('Arial', 9))
        
        # Espacio flexible al final
        spacer = ctk.CTkFrame(self.frameIndicadores, fg_color="transparent", height=10)
        spacer.grid(row=17, column=0, sticky="nsew")
        self.frameIndicadores.grid_rowconfigure(17, weight=1)
    
    def _create_bottom_bar(self):
        """Crea la barra inferior con parámetros críticos siempre visibles."""
        self.barraInferior = ctk.CTkFrame(self.principal, fg_color="#1a1a1a", height=60)
        self.barraInferior.grid(row=1, column=0, columnspan=2, padx=10, pady=(3, 6), sticky="ew")
        self.barraInferior.grid_propagate(False)

        for i in range(6):
            self.barraInferior.grid_columnconfigure(i, weight=1)

        self.campoRango = self._create_param_widget(self.barraInferior, "Rango", "80 km", 0)
        frame_ganancia = self._create_param_widget(self.barraInferior, "Ganancia", "0 dB", 1)
        self.campoGain = frame_ganancia
        self.campoGanancia = frame_ganancia
        self.campoInclinacion = self._create_param_widget(self.barraInferior, "Tilt", "0°", 2)
        self.campoTrack = self._create_param_widget(self.barraInferior, "Track", "0°", 3)
        frame_pv = self._create_param_widget(self.barraInferior, "Perfil V.", "OFF", 4)
        self.campoVp = frame_pv
        self.campoPV = frame_pv
        self._create_color_legend_compact(5)

    def _create_param_widget(self, parent, label, default_value, column):
        """Crea un widget de parámetro compacto para la barra inferior."""
        frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=6)
        frame.grid(row=0, column=column, padx=3, pady=6, sticky="nsew")

        lbl = ctk.CTkLabel(frame, text=label, font=('Arial', 8, 'bold'), text_color="#888")
        lbl.pack(pady=(4, 0))

        valor = ctk.CTkLabel(frame, text=default_value, font=('Arial', 12, 'bold'), text_color="white")
        valor.pack(pady=(0, 4))

        frame.valor_label = valor
        return frame

    def _create_color_legend_compact(self, column):
        """Crea una leyenda de colores compacta en una sola fila."""
        frame = ctk.CTkFrame(self.barraInferior, fg_color="#2a2a2a", corner_radius=6)
        frame.grid(row=0, column=column, padx=3, pady=6, sticky="nsew")

        colores_frame = ctk.CTkFrame(frame, fg_color="transparent")
        colores_frame.place(relx=0.5, rely=0.5, anchor="center")

        items = [
            ("#22c55e", "Dbl"),
            ("#eab308", "Mod"),
            ("#ef4444", "Fte"),
            ("#a855f7", "Sev"),
        ]
        for i, (hex_color, texto) in enumerate(items):
            dot = ctk.CTkFrame(colores_frame, width=8, height=8, corner_radius=4, fg_color=hex_color)
            dot.grid(row=i, column=0, padx=(2, 2), pady=1)
            dot.grid_propagate(False)
            ctk.CTkLabel(colores_frame, text=texto, font=('Arial', 7), text_color="#aaa").grid(row=i, column=1, padx=(0, 2), pady=0, sticky="w")
    
    def _update_param_widget(self, widget, value):
        """Actualiza el valor de un widget de parámetro."""
        if hasattr(widget, 'valor_label'):
            widget.valor_label.configure(text=value)
        elif hasattr(widget, 'configure'):
            # Fallback para CTkEntry (legacy)
            try:
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.insert(0, value)
                widget.configure(state="readonly")
            except:
                pass
    
    def _create_graph_panel(self):
        """Crea el panel derecho con el gráfico del radar."""
        # Frame para el gráfico
        self.frame_grafico = ctk.CTkFrame(self.principal, fg_color="#1a1a1a")
        self.frame_grafico.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        # Configurar grid para que el canvas ocupe todo el espacio
        self.frame_grafico.grid_rowconfigure(0, weight=1)
        self.frame_grafico.grid_columnconfigure(0, weight=1)
        
        # Inicializar el gráfico con tamaño adaptable
        self.grafico = self.grafico_class()
        self.fig = self.grafico.fig
        self.ax = self.grafico.ax
        
        # Ajustar figura para mejor visualización
        self.fig.set_tight_layout(True)
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        # Canvas para el gráfico (RESPONSIVO)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafico)
        self.canvas.draw()
        
        # Widget del canvas con configuración mejorada
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas_widget.configure(bg='#1a1a1a')
        
        # Configurar el canvas para que se redimensione con la ventana
        canvas_widget.bind("<Configure>", self._on_canvas_resize)
        
        logger.info("Panel de visualización responsivo creado exitosamente")
    
    def _on_canvas_resize(self, event):
        """Callback cuando el canvas se redimensiona."""
        try:
            # Obtener las nuevas dimensiones en pulgadas
            width_inches = event.width / self.fig.dpi
            height_inches = event.height / self.fig.dpi
            
            # Mantener proporción cuadrada para el radar
            min_size = min(width_inches, height_inches)
            
            # Solo actualizar si el cambio es significativo (más de 0.3 pulgadas)
            current_w = self.fig.get_figwidth()
            current_h = self.fig.get_figheight()
            
            if abs(current_w - min_size) > 0.3 or abs(current_h - min_size) > 0.3:
                # Usar el tamaño más pequeño para mantener proporción
                self.fig.set_size_inches(min_size, min_size, forward=True)
                self.fig.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)
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
                self.campoTemperatura.configure(text=f"{datos['temperatura']:.1f}°C")
            
            if 'humedad' in datos:
                self.campoHumedad.configure(text=f"{datos['humedad']:.1f}%")
            
            if 'presion' in datos:
                self.campoPresion.configure(text=f"{datos['presion']:.1f} hPa")
            
            if 'viento' in datos:
                self.campoViento.configure(text=f"{datos['viento']:.1f}m/s")
            
            if 'direccion_viento' in datos:
                self.campoDireccionViento.configure(text=f"{datos['direccion_viento']:.0f}°")
            
            if 'precipitacion' in datos:
                self.campoPrecipitacion.configure(text=f"{datos['precipitacion']:.2f}mm")
            
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
        import CargaSensor as CS
        
        tinicial = time.time()
        
        try:
            # Actualizar barrido
            self.barrido_actual = self.barrido_nuevo
            hilo = threading.Thread(target=self.nueva_lectura, daemon=True)
            hilo.start()
            
            # Usar ubicación del PC (ya obtenida al iniciar)
            # Si aún no se ha obtenido, intentar nuevamente en segundo plano
            if not self._ubicacion_pc_obtenida:
                threading.Thread(target=self._obtener_ubicacion_pc, daemon=True).start()
            
            # Obtener coordenadas de forma thread-safe
            with self._ubicacion_lock:
                lat = self.latitud
                lon = self.longitud
            
            # Orientación fija a 0 (sin brújula del radar, posición estática)
            self.compass = 0
            
            # Actualizar labels de GPS (ubicación del PC)
            self.labelCoordenadas2.configure(
                text=f"{round(lat, 5)}, {round(lon, 5)}"
            )
            self.labelDir2.configure(text=f"{self.compass}°")
            
            # Actualizar gráfico del radar (usar variables locales thread-safe)
            self.grafico.actualizar_grafico(
                self.barrido_actual,
                lat,
                lon,
                self.compass
            )
            self.canvas.draw_idle()
            
            # Guardar imágenes (opcional, comentado por rendimiento)
            # self.grafico.fig.savefig('radar.png', transparent=True)
            
            # Verificar si hay datos del radar disponibles
            if self.barrido_actual is None:
                # No hay datos - mostrar estado "sin datos"
                self.l_aceptacion.configure(
                    text="● Sin Datos",
                    text_color="orange"
                )
                self.l_STDBY.configure(text_color="gray")
                self.l_ON.configure(text_color="gray")
                self.l_TEST.configure(text_color="gray")
                
                # Limpiar campos de información
                self.campoFallos.configure(state="normal")
                self.campoFallos.delete("0.0", "end")
                self.campoFallos.insert("end", "Sin conexión al radar")
                self.campoFallos.configure(state="disabled")
                
                self.campoAnuncio.configure(state="normal")
                self.campoAnuncio.delete("0.0", "end")
                self.campoAnuncio.insert("end", "Esperando datos...")
                self.campoAnuncio.configure(state="disabled")
                
                # Valores por defecto en parámetros (barra inferior)
                self._update_param_widget(self.campoGanancia, "-- dB")
                self._update_param_widget(self.campoRango, "-- km")
                self._update_param_widget(self.campoInclinacion, "--°")
                self._update_param_widget(self.campoTrack, "--°")
                self._update_param_widget(self.campoVp, "--")
                
                # Programar siguiente actualización y salir
                if self._update_running:
                    self._update_id = self.root.after(1000, self.actualizar)
                return
            
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
            
            # Actualizar parámetros del radar (barra inferior)
            self._update_param_widget(self.campoGanancia, f"{self.barrido_actual.ganancia} dB")
            self._update_param_widget(self.campoRango, f"{self.barrido_actual.rango} km")
            self._update_param_widget(self.campoInclinacion, f"{self.barrido_actual.inclinacion}°")
            self._update_param_widget(self.campoTrack, f"{getattr(self.barrido_actual, 'track', 0)}°")
            
            # Perfil vertical
            pv_status = "ON" if 7 in getattr(self.barrido_actual, 'anuncio', []) else "OFF"
            self._update_param_widget(self.campoVp, pv_status)
            
            # Actualizar sensores meteorológicos (panel izquierdo)
            try:
                nombre_archivo = "CR310_RK900_10.csv"
                datosSensor = CS.obtener_ultima_lectura(nombre_archivo)
                
                if datosSensor:
                    # Temperatura
                    if 'Temperature' in datosSensor:
                        self.campoTemperatura.configure(text=f"{datosSensor.get('Temperature')}°C")
                    
                    # Humedad
                    if 'Humidity' in datosSensor:
                        self.campoHumedad.configure(text=f"{datosSensor.get('Humidity')}%")
                    
                    # Viento
                    if 'Wind_Speed' in datosSensor:
                        self.campoViento.configure(text=f"{datosSensor.get('Wind_Speed')}m/s")
                    
                    # Precipitación
                    if 'Precipitation' in datosSensor:
                        self.campoPrecipitacion.configure(text=f"{datosSensor.get('Precipitation')}mm")
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
            # Solo capturar si el módulo Captura está disponible (requiere saleae)
            if self.captura_disponible and self.cap is not None:
                self.cap.capturaDatos()
            
            datos = self.intp.main()
            if datos:
                with self.lock:
                    self.barrido_nuevo = self.barrido_class(datos)
        except FileNotFoundError as e:
            logger.warning(f"Archivo de lecturas no encontrado en nueva_lectura: {e}")
        except Exception as e:
            logger.error(f"Error en nueva_lectura: {e}")


# Alias para compatibilidad
panel_visualizacion = ResponsiveVisualizationPanel

