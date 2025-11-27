"""
Aplicación principal del Software Radar - Versión Responsiva.

Esta versión se adapta automáticamente a cualquier resolución de pantalla.
"""
import os
import sys
import customtkinter as ctk
from PIL import Image
import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

# Importar módulos legacy
from ComSerial import comunicacion


def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso.
    Funciona tanto en desarrollo como cuando está empaquetado con PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
        logger.debug(f"Ejecutando como ejecutable empaquetado: {base_path}")
    except AttributeError:
        # Desarrollo normal
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logger.debug(f"Ejecutando en modo desarrollo: {base_path}")
    
    return os.path.join(base_path, relative_path)


# Importar assets con soporte para ejecutable empaquetado
carpeta_imagenes = get_resource_path("assets/images")
if not os.path.exists(carpeta_imagenes):
    carpeta_imagenes = get_resource_path("imagenes")
    logger.debug(f"Usando carpeta imagenes: {carpeta_imagenes}")
else:
    logger.debug(f"Usando carpeta assets/images: {carpeta_imagenes}")


class ResponsiveRadarApp:
    """
    Aplicación de Radar con interfaz responsiva.
    
    Se adapta automáticamente a cualquier tamaño de pantalla.
    """
    
    def __init__(self):
        """Inicializa la aplicación responsiva."""
        logger.info("Iniciando aplicación responsiva")
        
        # Configuración de tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Software Radar")
        
        # Variables de estado
        self.current_panel = None
        self.objeto_control = None
        self.objeto_visualizacion = None
        self.objeto_mapa = None
        self.serial = comunicacion()
        
        # Configurar ventana responsiva
        self._setup_responsive_window()
        
        # Configurar UI
        self._setup_ui()
        
        # Bind para reajuste de ventana
        self.root.bind('<Configure>', self._on_window_resize)
        
        logger.info("Aplicación responsiva inicializada")
    
    def _setup_responsive_window(self):
        """Configura ventana para ser responsiva."""
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular tamaño de ventana (85% de la pantalla)
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # Establecer tamaño mínimo
        min_width = 1000
        min_height = 600
        self.root.minsize(min_width, min_height)
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configurar grid weights para responsividad
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)  # Contenedor principal expandible
        
        logger.info(f"Ventana configurada: {window_width}x{window_height}")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario responsiva."""
        # ==================== MENÚ LATERAL ====================
        self._create_sidebar()
        
        # ==================== CONTENEDOR PRINCIPAL ====================
        self._create_main_container()
        
        # ==================== PANTALLA DE BIENVENIDA ====================
        self._show_welcome_screen()
    
    def _create_sidebar(self):
        """Crea el menú lateral responsivo."""
        # Frame del menú
        self.menu = ctk.CTkFrame(
            self.root,
            fg_color="#1F6AA5",
            corner_radius=0
        )
        self.menu.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        
        # Configurar grid del menú
        self.menu.grid_rowconfigure(5, weight=1)  # Espacio flexible al final
        
        # ==================== LOGO/TÍTULO ====================
        title_frame = ctk.CTkFrame(self.menu, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(20, 30), padx=20, sticky="ew")
        
        title = ctk.CTkLabel(
            title_frame,
            text="R A D A R",
            font=("Arial Black", 24),
            text_color="white"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Sistema de Control",
            font=("Arial", 10),
            text_color="lightblue"
        )
        subtitle.pack()
        
        # ==================== BOTONES DE NAVEGACIÓN ====================
        # Cargar iconos con tamaño optimizado
        icon_size = (35, 35)  # Tamaño más compacto y profesional
        
        try:
            icon_control_img = Image.open(os.path.join(carpeta_imagenes, "Icono palanca.png"))
            self.icon_control = ctk.CTkImage(
                light_image=icon_control_img,
                dark_image=icon_control_img,
                size=icon_size
            )
        except:
            self.icon_control = None
            logger.warning("No se pudo cargar icono de control")
        
        try:
            icon_radar_img = Image.open(os.path.join(carpeta_imagenes, "Icono radar.png"))
            self.icon_radar = ctk.CTkImage(
                light_image=icon_radar_img,
                dark_image=icon_radar_img,
                size=icon_size
            )
        except:
            self.icon_radar = None
            logger.warning("No se pudo cargar icono de radar")
        
        # Botón Control - Diseño mejorado
        self.btn_control = ctk.CTkButton(
            self.menu,
            text="  Control",  # Espacio extra para separación del icono
            image=self.icon_control,
            compound="left",
            anchor="w",  # Alinear contenido a la izquierda
            font=("Arial", 15, "bold"),
            height=55,  # Más altura para mejor visualización
            corner_radius=10,
            fg_color="#2B5278",
            hover_color="#3D6A91",
            command=self.show_control_panel
        )
        self.btn_control.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        
        # Botón Visualización - Diseño mejorado
        self.btn_visualizacion = ctk.CTkButton(
            self.menu,
            text="  Visualización",  # Espacio extra para separación del icono
            image=self.icon_radar,
            compound="left",
            anchor="w",  # Alinear contenido a la izquierda
            font=("Arial", 15, "bold"),
            height=55,  # Más altura para mejor visualización
            corner_radius=10,
            fg_color="#2B5278",
            hover_color="#3D6A91",
            command=self.show_visualization_panel
        )
        self.btn_visualizacion.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        
        # Botón Mapa - Nuevo panel de mapa geográfico
        self.btn_mapa = ctk.CTkButton(
            self.menu,
            text="  🗺️ Mapa",  # Icono de mapa con texto
            compound="left",
            anchor="w",
            font=("Arial", 15, "bold"),
            height=55,
            corner_radius=10,
            fg_color="#2B5278",
            hover_color="#3D6A91",
            command=self.show_map_panel
        )
        self.btn_mapa.grid(row=3, column=0, pady=5, padx=10, sticky="ew")
        
        # ==================== INFO DE CONEXIÓN ====================
        self.connection_frame = ctk.CTkFrame(
            self.menu,
            fg_color="transparent",
            corner_radius=10
        )
        self.connection_frame.grid(row=6, column=0, pady=(10, 20), padx=20, sticky="sew")
        
        self.connection_indicator = ctk.CTkLabel(
            self.connection_frame,
            text="● Desconectado",
            font=("Arial", 10),
            text_color="red"
        )
        self.connection_indicator.pack(pady=5)
        
        # Actualizar indicador de conexión cada segundo
        self._update_connection_status()
    
    def _create_main_container(self):
        """Crea el contenedor principal responsivo."""
        self.container = ctk.CTkFrame(
            self.root,
            fg_color="#242424",
            corner_radius=0
        )
        self.container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Configurar grid para que sea totalmente responsivo
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
    
    def _show_welcome_screen(self):
        """Muestra pantalla de bienvenida responsiva."""
        welcome_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        welcome_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid
        welcome_frame.grid_rowconfigure(0, weight=1)
        welcome_frame.grid_rowconfigure(1, weight=0)
        welcome_frame.grid_rowconfigure(2, weight=1)
        welcome_frame.grid_columnconfigure(0, weight=1)
        
        # Logo de la facultad (si existe)
        try:
            logo_img = Image.open(os.path.join(carpeta_imagenes, "Icono fac.png"))
            
            # Calcular tamaño adaptativo (50% del contenedor)
            container_width = self.container.winfo_width()
            if container_width < 100:  # Si aún no se ha renderizado
                container_width = 800
            
            logo_width = int(container_width * 0.5)
            logo_height = int(logo_width * 0.6)  # Mantener proporción
            
            logo_ctk = ctk.CTkImage(
                light_image=logo_img,
                dark_image=logo_img,
                size=(logo_width, logo_height)
            )
            
            logo_label = ctk.CTkLabel(
                welcome_frame,
                text="",
                image=logo_ctk
            )
            logo_label.grid(row=1, column=0, pady=20)
            
            # Guardar referencia para evitar garbage collection
            self.welcome_logo = logo_ctk
        except Exception as e:
            logger.warning(f"No se pudo cargar logo: {e}")
            
            # Mostrar mensaje de bienvenida en su lugar
            welcome_text = ctk.CTkLabel(
                welcome_frame,
                text="Bienvenido a Software Radar",
                font=("Arial", 32, "bold"),
                text_color="white"
            )
            welcome_text.grid(row=1, column=0, pady=20)
        
        # Instrucciones
        instructions = ctk.CTkLabel(
            welcome_frame,
            text="Selecciona una opción del menú para comenzar",
            font=("Arial", 14),
            text_color="gray"
        )
        instructions.grid(row=2, column=0, sticky="n", pady=20)
        
        self.current_panel = welcome_frame
    
    def show_control_panel(self):
        """Muestra el panel de control responsivo."""
        logger.info("Mostrando panel de control responsivo")
        
        # CORRECCIÓN: Detener ciclos de actualización de otros paneles
        if self.objeto_visualizacion is not None and hasattr(self.objeto_visualizacion, 'detener'):
            self.objeto_visualizacion.detener()
        if self.objeto_mapa is not None and hasattr(self.objeto_mapa, 'detener'):
            self.objeto_mapa.detener()
        
        # Importar panel de control responsivo
        if self.objeto_control is None:
            try:
                from src.ui.panels import ResponsiveControlPanel
                self.objeto_control = ResponsiveControlPanel(self.root, self.container, self.serial)
                logger.info("Panel de control responsivo creado")
            except Exception as e:
                logger.error(f"Error al crear panel de control responsivo: {e}")
                logger.info("Intentando cargar versión legacy...")
                try:
                    from mejorada import panel_control
                    self.objeto_control = panel_control(self.root, self.container, self.serial)
                    logger.info("Panel de control legacy cargado como fallback")
                except Exception as e2:
                    logger.error(f"Error al cargar fallback: {e2}")
                    messagebox.showerror(
                        "Error",
                        f"No se pudo cargar el panel de control:\n{str(e)}\n\nFallback: {str(e2)}"
                    )
                    return
        
        # CORRECCIÓN: Limpiar contenedor antes de mostrar panel
        if self.current_panel:
            try:
                self.current_panel.grid_forget()
            except:
                pass
        
        # Limpiar cualquier widget residual en el contenedor
        for widget in self.container.winfo_children():
            try:
                widget.grid_forget()
            except:
                pass
        
        self.objeto_control.principal.grid(row=0, column=0, sticky="nsew")
        self.current_panel = self.objeto_control.principal
        
        # Destacar botón activo
        self._highlight_active_button(self.btn_control)
    
    def show_visualization_panel(self):
        """Muestra el panel de visualización responsivo."""
        logger.info("Mostrando panel de visualización responsivo")
        
        # Verificar conexión serial
        if not self.serial.status:
            messagebox.showerror(
                "Sin comunicación serial",
                "Establezca primero la comunicación serial desde el panel de Control"
            )
            return
        
        # Detener ciclo de actualización del mapa si está activo
        if self.objeto_mapa is not None and hasattr(self.objeto_mapa, 'detener'):
            self.objeto_mapa.detener()
        
        # Importar panel de visualización responsivo
        if self.objeto_visualizacion is None:
            try:
                from src.ui.panels import ResponsiveVisualizationPanel
                self.objeto_visualizacion = ResponsiveVisualizationPanel(
                    self.root,
                    self.container,
                    self.serial
                )
                self.objeto_visualizacion.iniciar()
                logger.info("Panel de visualización responsivo creado")
            except Exception as e:
                logger.error(f"Error al crear panel de visualización responsivo: {e}")
                logger.info("Intentando cargar versión legacy...")
                try:
                    from mejorada import panel_visualizacion
                    self.objeto_visualizacion = panel_visualizacion(
                        self.root,
                        self.container,
                        self.serial
                    )
                    self.objeto_visualizacion.iniciar()
                    logger.info("Panel de visualización legacy cargado como fallback")
                except Exception as e2:
                    logger.error(f"Error al cargar fallback: {e2}")
                    messagebox.showerror(
                        "Error",
                        f"No se pudo cargar el panel de visualización:\n{str(e)}\n\nFallback: {str(e2)}"
                    )
                    return
        
        # CORRECCIÓN: Limpiar contenedor antes de mostrar panel
        if self.current_panel:
            try:
                self.current_panel.grid_forget()
            except:
                pass
        
        # Limpiar cualquier widget residual en el contenedor
        for widget in self.container.winfo_children():
            try:
                widget.grid_forget()
            except:
                pass
        
        self.objeto_visualizacion.principal.grid(row=0, column=0, sticky="nsew")
        self.current_panel = self.objeto_visualizacion.principal
        
        # CORRECCIÓN: Reiniciar ciclo de actualización al mostrar el panel
        # (el método iniciar() ahora previene duplicados automáticamente)
        if hasattr(self.objeto_visualizacion, 'iniciar'):
            self.objeto_visualizacion.iniciar()
        
        # Destacar botón activo
        self._highlight_active_button(self.btn_visualizacion)
    
    def show_map_panel(self):
        """Muestra el panel de mapa geográfico responsivo."""
        logger.info("Mostrando panel de mapa geográfico")
        
        # Verificar conexión serial
        if not self.serial.status:
            messagebox.showerror(
                "Sin comunicación serial",
                "Establezca primero la comunicación serial desde el panel de Control"
            )
            return
        
        # Detener actualización del panel de visualización si está activo
        if self.objeto_visualizacion is not None and hasattr(self.objeto_visualizacion, 'detener'):
            self.objeto_visualizacion.detener()
        
        # Importar panel de mapa responsivo
        if self.objeto_mapa is None:
            try:
                from src.ui.panels import ResponsiveMapPanel
                self.objeto_mapa = ResponsiveMapPanel(
                    self.root,
                    self.container,
                    self.serial
                )
                self.objeto_mapa.iniciar()
                logger.info("Panel de mapa responsivo creado")
            except Exception as e:
                logger.error(f"Error al crear panel de mapa responsivo: {e}")
                messagebox.showerror(
                    "Error",
                    f"No se pudo cargar el panel de mapa:\n{str(e)}"
                )
                return
        
        # CORRECCIÓN: Limpiar contenedor antes de mostrar panel
        if self.current_panel:
            try:
                self.current_panel.grid_forget()
            except:
                pass
        
        # Limpiar cualquier widget residual en el contenedor
        for widget in self.container.winfo_children():
            try:
                widget.grid_forget()
            except:
                pass
        
        self.objeto_mapa.principal.grid(row=0, column=0, sticky="nsew")
        self.current_panel = self.objeto_mapa.principal
        
        # Reiniciar ciclo de actualización al mostrar el panel
        if hasattr(self.objeto_mapa, 'iniciar'):
            self.objeto_mapa.iniciar()
        
        # Destacar botón activo
        self._highlight_active_button(self.btn_mapa)
    
    def _highlight_active_button(self, active_button):
        """Destaca el botón activo."""
        # Restablecer todos los botones
        self.btn_control.configure(fg_color="#2B5278")
        self.btn_visualizacion.configure(fg_color="#2B5278")
        self.btn_mapa.configure(fg_color="#2B5278")
        
        # Destacar botón activo
        active_button.configure(fg_color="#4A90D9")
    
    def _update_connection_status(self):
        """Actualiza el indicador de estado de conexión."""
        if self.serial.status:
            self.connection_indicator.configure(
                text="● Conectado",
                text_color="lightgreen"
            )
        else:
            self.connection_indicator.configure(
                text="● Desconectado",
                text_color="red"
            )
        
        # Actualizar cada segundo
        self.root.after(1000, self._update_connection_status)
    
    def _on_window_resize(self, event):
        """Maneja el redimensionamiento de la ventana."""
        # Este método se puede usar para ajustes adicionales al redimensionar
        pass
    
    def run(self):
        """Ejecuta la aplicación."""
        logger.info("Iniciando mainloop")
        self.root.mainloop()
    
    def cleanup(self):
        """Limpia recursos antes de cerrar."""
        if self.serial.status:
            self.serial.desconectar()
        logger.info("Aplicación cerrada correctamente")


# Alias para compatibilidad
RadarApp = ResponsiveRadarApp

