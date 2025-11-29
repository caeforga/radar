"""
Panel de Mapa Responsivo para el Software Radar.

Este panel muestra un mapa interactivo con overlay de datos del radar.
El mapa ocupa todo el espacio y los datos se muestran como overlays.
"""
import customtkinter as ctk
import tkintermapview
import threading
import math
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class ResponsiveMapPanel:
    """Panel de mapa responsivo con overlay de datos del radar."""
    
    def __init__(self, root, contenedor, serial):
        """
        Inicializa el panel de mapa responsivo.
        
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
        self.principal = ctk.CTkFrame(self.contenedor, fg_color="#1a1a2e")
        # NOTA: NO hacemos grid aquí, se hace desde app_responsive.py
        
        # Configurar grid para que el mapa ocupe todo
        self.principal.grid_rowconfigure(0, weight=1)
        self.principal.grid_columnconfigure(0, weight=1)
        
        # Variables de estado del radar
        self.latitud = 4.7110      # Bogotá, Colombia
        self.longitud = -74.0721
        self.orientacion = 0
        self.rango = 80  # km
        self.ganancia = 0
        self.aceptacion = False
        self.operacion = "STDBY"
        
        # Variables de control de actualización
        self._update_id = None
        self._update_running = False
        self.lock = threading.Lock()
        
        # MODO DEMO: Para pruebas sin radar conectado
        self.demo_mode = False
        self.demo_angle = 0  # Ángulo de rotación para animación demo
        
        # Inicializar barrido
        self.barrido_actual = None
        try:
            self.barrido_nuevo = self.barrido_class(self.intp.main())
        except:
            self.barrido_nuevo = None
            
        # Inicializar datos de radar vacíos
        self.radar_data = np.zeros((360, 512))
        
        # Crear el colormap
        self._create_radar_colormap()
        
        # Configurar Matplotlib (Off-screen)
        self._setup_matplotlib()
        
        # Crear el mapa
        self._create_map_panel()
        
        # Crear overlays de información
        self._create_info_overlays()
        
        # Crear la leyenda de colores
        self._create_color_legend()
        
        # Crear botón de modo demo
        self._create_demo_button()
        
        logger.info("Panel de mapa responsivo creado exitosamente")

    def _create_radar_colormap(self):
        """Crea el colormap personalizado para el radar con transparencia."""
        # Definir colores RGBA (Red, Green, Blue, Alpha)
        # El primer color (valor 0) es totalmente transparente
        colors = [
            (0, 0, 0, 0),       # 0: Transparente
            (0, 0.3, 0, 0.8),   # 10: Verde muy oscuro
            (0, 0.5, 0, 0.9),   # 20: Verde
            (0, 1, 0, 1),       # 30: Verde brillante
            (1, 1, 0, 1),       # 40: Amarillo
            (1, 0.65, 0, 1),    # 50: Naranja
            (1, 0, 0, 1),       # 60: Rojo
            (1, 0, 1, 1),       # 70: Magenta
            (1, 1, 1, 1)        # 80+: Blanco
        ]
        self.radar_cmap = LinearSegmentedColormap.from_list('radar', colors, N=256)
        # Asegurar que valores bajos sean transparentes
        self.radar_cmap.set_under((0, 0, 0, 0))

    def _setup_matplotlib(self):
        """Configura la figura de Matplotlib para renderizado off-screen."""
        # Crear figura de Matplotlib
        # Tamaño fijo en pulgadas, dpi controla resolución
        self.fig = plt.figure(figsize=(6, 6), dpi=100, facecolor='none')
        self.fig.patch.set_alpha(0.0)  # Fondo totalmente transparente
        self.ax = self.fig.add_subplot(111, projection='polar')
        
        # Configurar el plot polar inicial
        self.ax.set_facecolor('none')
        self.fig.patch.set_facecolor('none')
        self.fig.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.0)
        
        # Configurar orientación (Norte arriba)
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)  # Sentido horario
        
        # Configurar rango (360 grados completos)
        self.ax.set_thetamin(0)
        self.ax.set_thetamax(360)
        
        # Configurar Grid Polar (Anillos y Ángulos)
        self.ax.grid(True, color='#00ff00', alpha=0.5, linestyle='-', linewidth=0.8)
        
        # Configurar etiquetas de ángulos (Azimut)
        self.ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], 
                               color='#00ff00', fontweight='bold', fontsize=9)
        
        # Configurar etiquetas de rango (Distancia)
        self.ax.set_yticklabels([])  # Limpiamos labels por defecto
        self.ax.tick_params(axis='y', colors='#00ff00', labelsize=8)
        
        # Eliminar spines (bordes) innecesarios pero dejar el círculo exterior
        self.ax.spines['polar'].set_visible(True)
        self.ax.spines['polar'].set_color('#00ff00')
        self.ax.spines['polar'].set_linewidth(1)
        self.ax.spines['polar'].set_alpha(0.5)
        
        # Título desactivado en el plot
        self.ax.set_title("")
        
        # Crear el mesh para el mapa de calor
        theta = np.linspace(0, 2*np.pi, 361)
        r = np.linspace(0, self.rango, 513)
        self.theta_grid, self.r_grid = np.meshgrid(theta, r)
        
        # Crear el pcolormesh inicial (mapa de calor)
        self.radar_mesh = self.ax.pcolormesh(
            self.theta_grid.T, 
            self.r_grid.T,
            self.radar_data,
            cmap=self.radar_cmap,
            vmin=0,
            vmax=80,
            shading='auto',
            zorder=1,
            alpha=0.8  # Transparencia del mapa de calor
        )
        
        # Indicador de orientación (línea de barrido)
        self.heading_line = self.ax.plot(
            [0, 0], [0, self.rango],
            color='#00ffff', linewidth=2, zorder=10
        )[0]
        
        # Inicializar canvas Agg
        self.canvas = FigureCanvasAgg(self.fig)
    
    def _create_map_panel(self):
        """Crea el widget del mapa que ocupa todo el panel."""
        # Crear el mapa
        self.map_widget = tkintermapview.TkinterMapView(
            self.principal,
            corner_radius=0,
            bg_color="#1a1a2e"
        )
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        
        # Configurar el mapa
        self.map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=y&hl=es&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=19
        )  # Híbrido de Google (lyrs=y) para ver etiquetas
        
        # Posición inicial
        self.map_widget.set_position(self.latitud, self.longitud)
        self.map_widget.set_zoom(10)
        
        # Marker del radar (Imagen superpuesta)
        self.radar_overlay_marker = None
        
        logger.info("Mapa inicializado correctamente")
    
    def _create_info_overlays(self):
        """Crea los overlays de información sobre el mapa."""
        # ========== OVERLAY SUPERIOR IZQUIERDO: UBICACIÓN ==========
        self.overlay_location = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.overlay_location.place(relx=0.01, rely=0.01, anchor="nw")
        
        # Título
        ctk.CTkLabel(
            self.overlay_location,
            text="📍 UBICACIÓN RADAR",
            font=('Arial', 14, 'bold'),
            text_color="#3b82f6"
        ).pack(padx=15, pady=(10, 5))
        
        # Coordenadas
        self.lbl_coords = ctk.CTkLabel(
            self.overlay_location,
            text="Lat: 0.00000°  Lon: 0.00000°",
            font=('Consolas', 12),
            text_color="white"
        )
        self.lbl_coords.pack(padx=15, pady=2)
        
        # Orientación
        self.lbl_orientation = ctk.CTkLabel(
            self.overlay_location,
            text="🧭 Orientación: 0°",
            font=('Arial', 12),
            text_color="#22c55e"
        )
        self.lbl_orientation.pack(padx=15, pady=(5, 10))
        
        # ========== OVERLAY SUPERIOR DERECHO: PARÁMETROS ==========
        self.overlay_params = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.overlay_params.place(relx=0.99, rely=0.01, anchor="ne")
        
        # Título
        ctk.CTkLabel(
            self.overlay_params,
            text="📊 PARÁMETROS",
            font=('Arial', 14, 'bold'),
            text_color="#3b82f6"
        ).pack(padx=15, pady=(10, 5))
        
        # Rango
        self.lbl_range = ctk.CTkLabel(
            self.overlay_params,
            text="📏 Rango: 80 km",
            font=('Arial', 12),
            text_color="white"
        )
        self.lbl_range.pack(padx=15, pady=2)
        
        # Ganancia
        self.lbl_gain = ctk.CTkLabel(
            self.overlay_params,
            text="📶 Ganancia: 0 dB",
            font=('Arial', 12),
            text_color="white"
        )
        self.lbl_gain.pack(padx=15, pady=2)
        
        # Estado de operación
        self.lbl_operation = ctk.CTkLabel(
            self.overlay_params,
            text="⏸ STDBY",
            font=('Arial', 12, 'bold'),
            text_color="#fbbf24"
        )
        self.lbl_operation.pack(padx=15, pady=(5, 10))
        
        # ========== OVERLAY INFERIOR IZQUIERDO: ACEPTACIÓN ==========
        self.overlay_status = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.overlay_status.place(relx=0.01, rely=0.99, anchor="sw")
        
        # Estado de aceptación
        self.lbl_accept = ctk.CTkLabel(
            self.overlay_status,
            text="● Sin Aceptación",
            font=('Arial', 14, 'bold'),
            text_color="#ef4444"
        )
        self.lbl_accept.pack(padx=15, pady=10)
        
        # ========== OVERLAY INFERIOR CENTRAL: ESCALA ==========
        self.overlay_scale = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.overlay_scale.place(relx=0.5, rely=0.99, anchor="s")
        
        # Escala de distancia
        self.lbl_scale = ctk.CTkLabel(
            self.overlay_scale,
            text="──── 25 km ────",
            font=('Consolas', 11),
            text_color="white"
        )
        self.lbl_scale.pack(padx=15, pady=8)
    
    def _create_color_legend(self):
        """Crea la leyenda de colores dBZ."""
        # Frame de leyenda
        self.overlay_legend = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.overlay_legend.place(relx=0.99, rely=0.5, anchor="e")
        
        # Título
        ctk.CTkLabel(
            self.overlay_legend,
            text="dBZ",
            font=('Arial', 11, 'bold'),
            text_color="white"
        ).pack(padx=8, pady=(8, 5))
        
        # Escala de colores dBZ (de mayor a menor intensidad)
        dbz_colors = [
            ("#FF00FF", "58+"),   # Magenta - Granizo
            ("#FF0000", "54"),    # Rojo intenso
            ("#FF4500", "50"),    # Rojo-naranja
            ("#FF8C00", "46"),    # Naranja
            ("#FFD700", "42"),    # Amarillo
            ("#FFFF00", "38"),    # Amarillo claro
            ("#00FF00", "34"),    # Verde
            ("#00CD00", "30"),    # Verde medio
            ("#008B00", "26"),    # Verde oscuro
            ("#00FFFF", "22"),    # Cyan
            ("#00BFFF", "18"),    # Azul claro
            ("#0000FF", "14"),    # Azul
            ("#00008B", "10"),    # Azul oscuro
        ]
        
        for color, value in dbz_colors:
            frame_item = ctk.CTkFrame(
                self.overlay_legend,
                fg_color=color,
                width=30,
                height=12,
                corner_radius=2
            )
            frame_item.pack(padx=8, pady=1)
            frame_item.pack_propagate(False)
            
            ctk.CTkLabel(
                frame_item,
                text=value,
                font=('Arial', 8),
                text_color="black" if color in ["#FFFF00", "#FFD700", "#00FF00", "#00FFFF"] else "white"
            ).pack(expand=True)
        
        # Separador
        ctk.CTkFrame(
            self.overlay_legend,
            height=1,
            fg_color="gray50"
        ).pack(fill="x", padx=5, pady=5)
        
        # Leyenda de tipos de precipitación
        legend_items = [
            ("🌧", "Lluvia"),
            ("⛈", "Tormenta"),
            ("🌨", "Granizo"),
        ]
        
        for emoji, text in legend_items:
            ctk.CTkLabel(
                self.overlay_legend,
                text=f"{emoji} {text}",
                font=('Arial', 9),
                text_color="white"
            ).pack(padx=8, pady=1)
        
        # Padding final
        ctk.CTkLabel(
            self.overlay_legend,
            text="",
            height=5
        ).pack()
    
    def _create_demo_button(self):
        """Crea el botón para activar el modo demo."""
        # Frame para el botón de demo
        self.demo_frame = ctk.CTkFrame(
            self.principal,
            fg_color=("#000000", "#000000"),
            bg_color="transparent",
            corner_radius=10
        )
        self.demo_frame.place(relx=0.5, rely=0.01, anchor="n")
        
        # Botón de modo demo
        self.btn_demo = ctk.CTkButton(
            self.demo_frame,
            text="🎮 Activar Demo",
            font=('Arial', 12, 'bold'),
            fg_color="#22c55e",
            hover_color="#16a34a",
            height=35,
            width=150,
            command=self._toggle_demo_mode
        )
        self.btn_demo.pack(padx=10, pady=10)
        
        # Label de estado demo
        self.lbl_demo_status = ctk.CTkLabel(
            self.demo_frame,
            text="",
            font=('Arial', 10),
            text_color="#fbbf24"
        )
        self.lbl_demo_status.pack(padx=10, pady=(0, 5))
    
    def _toggle_demo_mode(self):
        """Activa/desactiva el modo demo."""
        if self.demo_mode:
            # Desactivar demo
            self.demo_mode = False
            self._update_running = False
            if self._update_id:
                self.root.after_cancel(self._update_id)
                self._update_id = None
            
            self.btn_demo.configure(
                text="🎮 Activar Demo",
                fg_color="#22c55e",
                hover_color="#16a34a"
            )
            self.lbl_demo_status.configure(text="")
            
            # Limpiar radar
            self.radar_data = np.zeros((360, 512))
            self._update_radar_overlay()
            
            logger.info("Modo demo desactivado")
        else:
            # Activar demo
            self.demo_mode = True
            self.demo_angle = 0
            
            self.btn_demo.configure(
                text="⏹ Detener Demo",
                fg_color="#ef4444",
                hover_color="#dc2626"
            )
            self.lbl_demo_status.configure(text="🔴 MODO SIMULACIÓN ACTIVO")
            
            # Iniciar actualización demo
            self._iniciar_demo()
            
            logger.info("Modo demo activado")
    
    def _iniciar_demo(self):
        """Inicia el ciclo de actualización del modo demo."""
        if not self.demo_mode:
            return
        
        self._update_running = True
        self._actualizar_demo()
    
    def _actualizar_demo(self):
        """Actualiza los datos simulados del modo demo."""
        import random
        
        if not self.demo_mode:
            return
        
        try:
            # ===== DATOS SIMULADOS =====
            
            # Ubicación demo: Bogotá (fija)
            self.latitud = 4.7110
            self.longitud = -74.0721
            
            # Orientación que rota lentamente (simulando barrido)
            self.demo_angle = (self.demo_angle + 3) % 360
            self.orientacion = self.demo_angle
            
            # Rango variable
            self.rango = random.choice([40, 60, 80, 120, 240])
            
            # Ganancia aleatoria
            self.ganancia = random.randint(0, 50)
            
            # Alternar aceptación
            self.aceptacion = random.random() > 0.2  # 80% aceptado
            
            # Estado de operación
            self.operacion = random.choice(["ON", "ON", "ON", "TEST"])  # Mayormente ON
            
            # Generar datos de precipitación simulados
            self._generate_demo_precipitation()
            
            # ===== ACTUALIZAR UI =====
            self._update_overlays()
            self._update_radar_overlay()
            
        except Exception as e:
            logger.error(f"Error en actualización demo: {e}")
        
        # Programar próxima actualización (cada 200ms para animación más fluida)
        if self.demo_mode and self._update_running:
            self._update_id = self.root.after(200, self._actualizar_demo)
    
    def _generate_demo_precipitation(self):
        """Genera datos de precipitación simulados para el demo."""
        import random
        
        # Crear celdas de tormenta aleatorias
        num_storms = random.randint(2, 5)
        
        # Limpiar datos anteriores gradualmente (efecto de estela)
        self.radar_data = self.radar_data * 0.9
        
        for _ in range(num_storms):
            # Posición de la tormenta
            storm_angle = random.randint(0, 359)
            storm_range = random.randint(20, int(self.rango * 0.8))
            
            # Tamaño e intensidad
            storm_size_angle = random.randint(10, 40)
            storm_size_range = random.randint(10, 30)
            intensity = random.uniform(20, 70)
            
            # Dibujar la tormenta (aproximación simple)
            for da in range(-storm_size_angle//2, storm_size_angle//2):
                for dr in range(-storm_size_range//2, storm_size_range//2):
                    a = (storm_angle + da) % 360
                    r = int(storm_range + dr)
                    
                    if 0 <= r < 512:
                        # Calcular intensidad con gradiente
                        dist = math.sqrt(da**2 + dr**2)
                        max_dist = math.sqrt((storm_size_angle/2)**2 + (storm_size_range/2)**2)
                        falloff = max(0, 1 - dist / max_dist)
                        
                        value = intensity * falloff * random.uniform(0.8, 1.2)
                        self.radar_data[a, r] = max(self.radar_data[a, r], value)
    
    def _update_radar_overlay(self):
        """Actualiza el overlay visual del radar en el mapa."""
        try:
            # Actualizar posición del mapa (si cambió)
            if self.latitud != 0 and self.longitud != 0:
                self.map_widget.set_position(self.latitud, self.longitud)
            
            # Actualizar plot de Matplotlib
            self.ax.set_ylim(0, self.rango)
            
            # Recalcular grid si cambió el rango
            theta = np.linspace(0, 2*np.pi, 361)
            r = np.linspace(0, self.rango, 513)
            self.theta_grid, self.r_grid = np.meshgrid(theta, r)
            
            # Actualizar mesh
            self.radar_mesh.set_array(self.radar_data.ravel())
            
            # Forzar redibujado de la malla con las nuevas coordenadas
            # Es más eficiente borrar y crear nuevo mesh si cambian las dimensiones, 
            # pero set_array es más rápido para solo datos. 
            # Si rango cambia, necesitamos reconfigurar.
            
            # Simplificación: recrear mesh si rango cambia
            self.radar_mesh.remove()
            self.radar_mesh = self.ax.pcolormesh(
                self.theta_grid.T, 
                self.r_grid.T,
                self.radar_data,
                cmap=self.radar_cmap,
                vmin=0,
                vmax=80,
                shading='auto',
                zorder=1,
                alpha=0.8
            )
            
            # Actualizar línea de orientación
            heading_rad = np.deg2rad(self.orientacion)
            self.heading_line.set_data([heading_rad, heading_rad], [0, self.rango])
            
            # Actualizar anillos de rango (grid polar)
            # Calcular divisiones de rango
            if self.rango <= 40:
                step = 10
            elif self.rango <= 80:
                step = 20
            elif self.rango <= 120:
                step = 25
            else:
                step = 50
            
            rings = np.arange(step, self.rango + step, step)
            self.ax.set_rgrids(rings, labels=[f'{int(r)}' for r in rings], 
                              angle=45, color='#00ff00', fontsize=8, fontweight='bold')
            
            # Renderizar a imagen
            self.canvas.draw()
            rgba_buffer = self.canvas.buffer_rgba()
            width, height = self.fig.get_size_inches() * self.fig.get_dpi()
            image = Image.frombuffer("RGBA", (int(width), int(height)), rgba_buffer, "raw", "RGBA", 0, 1)
            
            # Convertir a PhotoImage para Tkinter
            radar_image_tk = ImageTk.PhotoImage(image)
            
            # Actualizar el marcador en el mapa
            if self.radar_overlay_marker:
                self.radar_overlay_marker.delete()
            
            # Usar un marcador personalizado con la imagen del radar
            self.radar_overlay_marker = self.map_widget.set_marker(
                self.latitud,
                self.longitud,
                icon=radar_image_tk,
                text="" # Sin texto
            )
            
            # Mantener referencia para evitar Garbage Collection
            self.radar_image_ref = radar_image_tk
            
        except Exception as e:
            logger.error(f"Error al actualizar overlay del radar: {e}")
    
    def _update_overlays(self):
        """Actualiza los textos de los overlays con los datos actuales."""
        try:
            # Actualizar coordenadas
            self.lbl_coords.configure(
                text=f"Lat: {self.latitud:.5f}°  Lon: {self.longitud:.5f}°"
            )
            
            # Actualizar orientación
            self.lbl_orientation.configure(
                text=f"🧭 Orientación: {self.orientacion:.1f}°"
            )
            
            # Actualizar rango
            self.lbl_range.configure(
                text=f"📏 Rango: {self.rango} km"
            )
            
            # Actualizar ganancia
            self.lbl_gain.configure(
                text=f"📶 Ganancia: {self.ganancia} dB"
            )
            
            # Actualizar estado de operación
            if self.operacion == "ON":
                self.lbl_operation.configure(
                    text="▶ ON",
                    text_color="#22c55e"
                )
            elif self.operacion == "TEST":
                self.lbl_operation.configure(
                    text="⚠ TEST",
                    text_color="#f59e0b"
                )
            else:
                self.lbl_operation.configure(
                    text="⏸ STDBY",
                    text_color="#fbbf24"
                )
            
            # Actualizar estado de aceptación
            if self.aceptacion:
                self.lbl_accept.configure(
                    text="● Aceptado",
                    text_color="#22c55e"
                )
            else:
                self.lbl_accept.configure(
                    text="● Sin Aceptación",
                    text_color="#ef4444"
                )
                
        except Exception as e:
            logger.error(f"Error al actualizar overlays: {e}")
    
    # ==================== MÉTODOS DE ACTUALIZACIÓN AUTOMÁTICA ====================
    
    def iniciar(self):
        """Inicia el ciclo de actualización automática."""
        if self._update_running:
            logger.warning("Ciclo de actualización del mapa ya está corriendo")
            return
        
        logger.info("Iniciando ciclo de actualización del panel de mapa")
        self._update_running = True
        self._update_id = self.root.after(2000, self.actualizar)
    
    def actualizar(self):
        """Actualiza todos los componentes del panel con nueva información."""
        import time
        import GPS
        
        try:
            # Actualizar barrido
            self.barrido_actual = self.barrido_nuevo
            hilo = threading.Thread(target=self.nueva_lectura, daemon=True)
            hilo.start()
            
            # Leer datos GPS y brújula
            self.serial.leer_datos()
            gps1 = self.serial.datos_recibidos.get()
            
            self.serial.leer_datos()
            gps2 = self.serial.datos_recibidos.get()
            
            self.serial.leer_datos()
            compass = self.serial.datos_recibidos.get()
            
            gps1_data = GPS.main(gps1)
            gps2_data = GPS.main(gps2)
            
            self.serial.arduino.reset_input_buffer()
            
            # Procesar coordenadas GPS
            if (gps1_data.get("fix_quality") == 0 or 
                gps1_data.get("satellites_in_use", 0) < 4 or 
                gps2_data.get("status") == 'V'):
                # Mantener últimas coordenadas válidas o usar default si es 0
                if self.latitud == 0:
                    self.latitud = 4.7110
                    self.longitud = -74.0721
            else:
                self.latitud = float(gps1_data.get("latitude", 0))
                self.longitud = float(gps1_data.get("longitude", 0))
            
            # Actualizar orientación
            try:
                self.orientacion = int(compass) if compass else 0
            except:
                self.orientacion = 0
            
            # Actualizar datos del barrido
            if self.barrido_actual:
                self.rango = self.barrido_actual.rango
                self.ganancia = self.barrido_actual.ganancia
                self.aceptacion = self.barrido_actual.aceptacion == 1
                
                # Determinar modo de operación
                if self.barrido_actual.operacion == 0:
                    self.operacion = "STDBY"
                elif self.barrido_actual.operacion == 1:
                    self.operacion = "ON"
                elif self.barrido_actual.operacion == 4:
                    self.operacion = "TEST"
                
                # Convertir datos a radar_data para el display
                self._convert_sweep_to_radar_data()
            
            # Actualizar interfaz
            self._update_overlays()
            self._update_radar_overlay()
            
        except Exception as e:
            logger.error(f"Error durante actualización del mapa: {e}", exc_info=True)
        
        # Programar próxima actualización solo si el ciclo está activo
        if self._update_running:
            self._update_id = self.root.after(2000, self.actualizar)
    
    def _convert_sweep_to_radar_data(self):
        """Convierte los datos del barrido a la matriz de radar."""
        if not self.barrido_actual or not hasattr(self.barrido_actual, 'radios'):
            return
        
        # Mapeo de valores de eco a dBZ aproximados
        echo_to_dbz = {
            0: 0,      # Sin eco
            1: 20,     # Eco débil
            2: 40,     # Eco moderado
            3: 55,     # Eco fuerte
            4: 70      # Eco muy intenso
        }
        
        try:
            for angulo, radio in self.barrido_actual.radios.items():
                # Convertir ángulo (-49 a 49) a índice (0 a 359)
                # El radar cubre ±49° desde la orientación
                angle_idx = (self.orientacion + angulo) % 360
                
                for i, valor in enumerate(radio.datos):
                    if i < 512 and valor in echo_to_dbz:
                        self.radar_data[angle_idx, i] = echo_to_dbz[valor]
        except Exception as e:
            logger.error(f"Error convirtiendo datos: {e}")

    def detener(self):
        """Detiene el ciclo de actualización automática."""
        logger.info("Deteniendo ciclo de actualización del panel de mapa")
        self._update_running = False
        
        if self._update_id is not None:
            try:
                self.root.after_cancel(self._update_id)
                self._update_id = None
                logger.info("Timer de actualización del mapa cancelado exitosamente")
            except Exception as e:
                logger.warning(f"Error al cancelar timer del mapa: {e}")
    
    def nueva_lectura(self):
        """Lee nuevos datos en un hilo separado."""
        try:
            import time
            time.sleep(5)
            with self.lock:
                self.barrido_nuevo = self.barrido_class(self.intp.main())
        except Exception as e:
            logger.error(f"Error en nueva_lectura del mapa: {e}")
    
    # ==================== MÉTODOS DE CONTROL DEL MAPA ====================
    
    def set_tile_server(self, server_type="satellite"):
        """
        Cambia el servidor de tiles del mapa.
        
        Args:
            server_type: Tipo de mapa ('satellite', 'street', 'terrain')
        """
        servers = {
            "satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
            "street": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
            "terrain": "https://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}&s=Ga",
            "hybrid": "https://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga",
            "osm": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
        }
        
        if server_type in servers:
            self.map_widget.set_tile_server(servers[server_type], max_zoom=19)
            logger.info(f"Servidor de tiles cambiado a: {server_type}")
    
    def zoom_to_radar(self):
        """Centra el mapa en la ubicación del radar."""
        if self.latitud != 0 and self.longitud != 0:
            self.map_widget.set_position(self.latitud, self.longitud)
            # Calcular zoom basado en el rango
            if self.rango <= 40:
                zoom = 10
            elif self.rango <= 80:
                zoom = 9
            elif self.rango <= 120:
                zoom = 8
            else:
                zoom = 7
            self.map_widget.set_zoom(zoom)


# Alias para compatibilidad
panel_mapa = ResponsiveMapPanel
