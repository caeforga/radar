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
        self.latitud = 0.0
        self.longitud = 0.0
        self.orientacion = 0
        self.rango = 80  # km
        self.ganancia = 0
        self.aceptacion = False
        self.operacion = "STDBY"
        
        # Variables de control de actualización
        self._update_id = None
        self._update_running = False
        self.lock = threading.Lock()
        
        # Inicializar barrido
        self.barrido_actual = None
        self.barrido_nuevo = self.barrido_class(self.intp.main())
        
        # Crear el mapa
        self._create_map_panel()
        
        # Crear overlays de información
        self._create_info_overlays()
        
        # Crear la leyenda de colores
        self._create_color_legend()
        
        logger.info("Panel de mapa responsivo creado exitosamente")
    
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
            "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=19
        )  # Satélite de Google
        
        # Posición inicial (se actualizará con GPS)
        # Coordenadas de Argentina como default
        self.map_widget.set_position(-34.6037, -58.3816)
        self.map_widget.set_zoom(8)
        
        # Marker del radar
        self.radar_marker = None
        
        # Círculos de rango
        self.range_circles = []
        
        # Polígono del sector del radar
        self.radar_polygon = None
        
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
    
    def _update_radar_overlay(self):
        """Actualiza el overlay visual del radar en el mapa."""
        try:
            # Limpiar elementos anteriores
            self._clear_radar_elements()
            
            if self.latitud == 0 and self.longitud == 0:
                return
            
            # Actualizar posición del mapa
            self.map_widget.set_position(self.latitud, self.longitud)
            
            # Agregar marker del radar
            self.radar_marker = self.map_widget.set_marker(
                self.latitud,
                self.longitud,
                text="📡 RADAR",
                font=('Arial', 10, 'bold'),
                text_color="white",
                marker_color_circle="#3b82f6",
                marker_color_outside="#1e40af"
            )
            
            # Dibujar círculos de rango
            self._draw_range_circles()
            
            # Dibujar sector del radar (cono de cobertura)
            self._draw_radar_sector()
            
        except Exception as e:
            logger.error(f"Error al actualizar overlay del radar: {e}")
    
    def _clear_radar_elements(self):
        """Limpia los elementos del radar del mapa."""
        try:
            # Eliminar marker
            if self.radar_marker:
                self.radar_marker.delete()
                self.radar_marker = None
            
            # Eliminar círculos de rango
            for circle in self.range_circles:
                try:
                    circle.delete()
                except:
                    pass
            self.range_circles = []
            
            # Eliminar polígono del sector
            if self.radar_polygon:
                try:
                    self.radar_polygon.delete()
                except:
                    pass
                self.radar_polygon = None
                
        except Exception as e:
            logger.debug(f"Error al limpiar elementos: {e}")
    
    def _draw_range_circles(self):
        """Dibuja círculos de rango alrededor del radar."""
        try:
            # Dibujar círculos a diferentes distancias
            distances = [25, 50, 75, self.rango]  # km
            
            for dist in distances:
                # Crear círculo usando polígono
                points = self._calculate_circle_points(
                    self.latitud,
                    self.longitud,
                    dist,
                    36  # número de puntos
                )
                
                if points:
                    circle = self.map_widget.set_polygon(
                        points,
                        fill_color=None,
                        outline_color="#3b82f680" if dist != self.rango else "#22c55e80",
                        border_width=1 if dist != self.rango else 2
                    )
                    self.range_circles.append(circle)
                    
        except Exception as e:
            logger.error(f"Error al dibujar círculos de rango: {e}")
    
    def _draw_radar_sector(self):
        """Dibuja el sector de cobertura del radar."""
        try:
            # Calcular puntos del sector (90° de apertura centrado en la orientación)
            apertura = 90  # grados
            inicio = self.orientacion - apertura / 2
            fin = self.orientacion + apertura / 2
            
            # Puntos del arco
            points = [(self.latitud, self.longitud)]  # Centro
            
            for angle in range(int(inicio), int(fin) + 1, 5):
                lat, lon = self._calculate_destination(
                    self.latitud,
                    self.longitud,
                    self.rango,
                    angle
                )
                points.append((lat, lon))
            
            points.append((self.latitud, self.longitud))  # Volver al centro
            
            if len(points) > 2:
                self.radar_polygon = self.map_widget.set_polygon(
                    points,
                    fill_color="#22c55e20",
                    outline_color="#22c55e80",
                    border_width=2
                )
                
        except Exception as e:
            logger.error(f"Error al dibujar sector del radar: {e}")
    
    def _calculate_circle_points(self, lat, lon, radius_km, num_points):
        """Calcula los puntos de un círculo en coordenadas geográficas."""
        points = []
        for i in range(num_points):
            angle = (360 / num_points) * i
            new_lat, new_lon = self._calculate_destination(lat, lon, radius_km, angle)
            points.append((new_lat, new_lon))
        points.append(points[0])  # Cerrar el círculo
        return points
    
    def _calculate_destination(self, lat, lon, distance_km, bearing):
        """
        Calcula las coordenadas de destino dado un punto, distancia y dirección.
        
        Args:
            lat: Latitud inicial
            lon: Longitud inicial
            distance_km: Distancia en kilómetros
            bearing: Dirección en grados (0 = Norte)
        
        Returns:
            Tuple (lat, lon) del punto destino
        """
        R = 6371  # Radio de la Tierra en km
        
        lat1 = math.radians(lat)
        lon1 = math.radians(lon)
        bearing_rad = math.radians(bearing)
        d = distance_km / R
        
        lat2 = math.asin(
            math.sin(lat1) * math.cos(d) +
            math.cos(lat1) * math.sin(d) * math.cos(bearing_rad)
        )
        
        lon2 = lon1 + math.atan2(
            math.sin(bearing_rad) * math.sin(d) * math.cos(lat1),
            math.cos(d) - math.sin(lat1) * math.sin(lat2)
        )
        
        return math.degrees(lat2), math.degrees(lon2)
    
    def _update_overlays(self):
        """Actualiza los textos de los overlays con los datos actuales."""
        try:
            # Actualizar coordenadas
            self.lbl_coords.configure(
                text=f"Lat: {self.latitud:.5f}°  Lon: {self.longitud:.5f}°"
            )
            
            # Actualizar orientación
            self.lbl_orientation.configure(
                text=f"🧭 Orientación: {self.orientacion}°"
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
                self.latitud = 0
                self.longitud = 0
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
            
            # Actualizar interfaz
            self._update_overlays()
            self._update_radar_overlay()
            
        except Exception as e:
            logger.error(f"Error durante actualización del mapa: {e}", exc_info=True)
        
        # Programar próxima actualización solo si el ciclo está activo
        if self._update_running:
            self._update_id = self.root.after(2000, self.actualizar)
    
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

