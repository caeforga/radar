"""
Panel de Control Responsivo para el Software Radar.

Este panel se adapta automáticamente al tamaño del contenedor.
"""
import customtkinter as ctk
from tkinter import messagebox
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import roboticstoolbox as rtb
import logging

logger = logging.getLogger(__name__)

matplotlib.use('Agg')


class ResponsiveControlPanel:
    """Panel de control responsivo con todos los controles del radar."""
    
    def __init__(self, root, contenedor, serial):
        """
        Inicializa el panel de control responsivo.
        
        Args:
            root: Ventana principal
            contenedor: Frame contenedor
            serial: Objeto de comunicación serial
        """
        self.root = root
        self.contenedor = contenedor
        self.datos_arduino = serial
        self.port = self.datos_arduino.puertos
        self.baud = self.datos_arduino.baudrates
        
        # Frame principal RESPONSIVO
        self.principal = ctk.CTkFrame(self.contenedor, fg_color="#242424")
        # NOTA: NO hacemos grid aquí, se hace desde app_responsive.py
        
        # Configurar grid para responsividad
        self.principal.grid_rowconfigure(0, weight=2)  # Área superior (robot + serial)
        self.principal.grid_rowconfigure(1, weight=1)  # Área inferior (controles)
        self.principal.grid_columnconfigure(0, weight=3)  # Columna izquierda (robot)
        self.principal.grid_columnconfigure(1, weight=1)  # Columna derecha (serial)
        
        # Variables de estado
        self.flag = 0
        self.flagsliders1 = 0
        self.flagsliders2 = 0
        self.orientacion = 0
        self.anguloTrack = 0
        self.rango = 80
        self.perfil = 0
        
        # Crear UI
        self._create_robot_section()
        self._create_serial_section()
        self._create_controls_section()
    
    def _create_robot_section(self):
        """Crea la sección del robot y sliders responsiva."""
        # Frame del robot (área principal izquierda)
        self.framePolla = ctk.CTkFrame(self.principal)
        self.framePolla.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid
        self.framePolla.grid_rowconfigure(0, weight=1)  # Área del gráfico
        self.framePolla.grid_rowconfigure(1, weight=0)  # Controles
        self.framePolla.grid_columnconfigure(0, weight=1)  # Área principal
        self.framePolla.grid_columnconfigure(1, weight=0)  # Slider vertical
        
        # ========== GRÁFICO DEL ROBOT 3D ==========
        self.frameGG = ctk.CTkFrame(self.framePolla)
        self.frameGG.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        try:
            self.robot = rtb.SerialLink([
                rtb.RevoluteDH(d=0.23, alpha=-np.pi/2, offset=0),
                rtb.RevoluteDH(a=0.5, offset=-np.pi/2)
            ], name='Radar')
            
            self.robot.plot([0, 0], limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])
            self.fig = plt.gcf()
            self.ax = plt.gca()
            self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
            self.ax.plot([0, 1], [0, 0], [0, 0])
            
            self.frameGG.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.frameGG.canvas.draw()
        except Exception as e:
            logger.error(f"Error al crear robot 3D: {e}")
            label_error = ctk.CTkLabel(
                self.frameGG,
                text="Robot 3D\n(requiere roboticstoolbox)",
                font=("Arial", 14),
                text_color="gray"
            )
            label_error.pack(expand=True)
        
        # ========== SLIDER HORIZONTAL (Rotación) ==========
        slider_h_frame = ctk.CTkFrame(self.framePolla, fg_color="transparent")
        slider_h_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        slider_h_frame.grid_columnconfigure(0, weight=1)
        
        self.Label1 = ctk.CTkLabel(
            slider_h_frame,
            text='Motor de Rotación',
            font=('Arial', 13, 'bold')
        )
        self.Label1.grid(row=0, column=0, pady=(0, 5))
        
        self.slider1 = ctk.CTkSlider(
            slider_h_frame,
            from_=-180, to=180,
            orientation="horizontal",
            state="disabled",
            command=self.actualizar_valor
        )
        self.slider1.set(0)
        self.slider1.grid(row=1, column=0, sticky="ew", padx=20)
        self.slider1.bind("<ButtonRelease-1>", self.on_scale_release)
        
        self.entry1 = ctk.CTkEntry(
            slider_h_frame,
            width=80,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entry1.grid(row=2, column=0, pady=(5, 0))
        
        # ========== SLIDER VERTICAL (Inclinación) ==========
        slider_v_frame = ctk.CTkFrame(self.framePolla, fg_color="transparent")
        slider_v_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="ns")
        slider_v_frame.grid_rowconfigure(1, weight=1)
        
        self.Label2 = ctk.CTkLabel(
            slider_v_frame,
            text='Motor de\nInclinación',
            font=('Arial', 11, 'bold')
        )
        self.Label2.grid(row=0, column=0, pady=(0, 10))
        
        self.slider2 = ctk.CTkSlider(
            slider_v_frame,
            from_=-60, to=60,
            orientation="vertical",
            state="disabled",
            command=self.actualizar_valor
        )
        self.slider2.set(0)
        self.slider2.grid(row=1, column=0, sticky="ns")
        self.slider2.bind("<ButtonRelease-1>", self.on_scale_release)
        
        self.entry2 = ctk.CTkEntry(
            slider_v_frame,
            width=60,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entry2.grid(row=2, column=0, pady=(10, 0))
    
    def _create_serial_section(self):
        """Crea la sección de configuración serial responsiva."""
        self.frameCock = ctk.CTkFrame(self.principal)
        self.frameCock.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            self.frameCock,
            text="Configuración Serial",
            font=('Arial', 16, 'bold')
        )
        title.grid(row=0, column=0, pady=(10, 20), padx=10)
        
        # Puertos COM
        ctk.CTkLabel(
            self.frameCock,
            text='Puerto COM',
            font=('Arial', 12, 'bold')
        ).grid(row=1, column=0, padx=10, pady=(10, 5))
        
        self.combobox_port = ctk.CTkComboBox(
            self.frameCock,
            justify='center',
            font=('Arial', 12)
        )
        self.actualizar_puertos()
        self.combobox_port.grid(row=2, column=0, pady=(0, 15), padx=10, sticky="ew")
        
        # Baud Rate
        ctk.CTkLabel(
            self.frameCock,
            text='Baud Rate',
            font=('Arial', 12, 'bold')
        ).grid(row=3, column=0, padx=10, pady=(10, 5))
        
        self.combobox_baud = ctk.CTkComboBox(
            self.frameCock,
            values=self.baud,
            justify='center',
            font=('Arial', 12)
        )
        self.combobox_baud.grid(row=4, column=0, pady=(0, 20), padx=10, sticky="ew")
        self.combobox_baud.set("9600")
        
        # Botones de conexión con paleta profesional
        self.bt_conectar = ctk.CTkButton(
            self.frameCock,
            text='🔌 Conectar',
            font=('Arial', 13, 'bold'),
            fg_color='#16a34a',  # Verde profesional
            hover_color='#15803d',
            height=40,
            command=self.conectar_serial
        )
        self.bt_conectar.grid(row=5, column=0, pady=5, padx=10, sticky="ew")
        
        self.bt_actualizar = ctk.CTkButton(
            self.frameCock,
            text='🔄 Actualizar Puertos',
            font=('Arial', 13, 'bold'),
            fg_color='#475569',  # Gris neutro para acciones secundarias
            hover_color='#334155',
            height=40,
            command=self.actualizar_puertos
        )
        self.bt_actualizar.grid(row=6, column=0, pady=5, padx=10, sticky="ew")
        
        self.bt_desconectar = ctk.CTkButton(
            self.frameCock,
            text='❌ Desconectar',
            font=('Arial', 13, 'bold'),
            fg_color='#dc2626',  # Rojo sobrio para acciones destructivas
            hover_color='#991b1b',
            height=40,
            command=self.desconectar_serial,
            state='disabled'
        )
        self.bt_desconectar.grid(row=7, column=0, pady=5, padx=10, sticky="ew")
        
        # Estado de conexión
        self.label_estado = ctk.CTkLabel(
            self.frameCock,
            text="● Desconectado",
            font=('Arial', 11),
            text_color="red"
        )
        self.label_estado.grid(row=8, column=0, pady=(20, 10), padx=10)
    
    def _create_controls_section(self):
        """Crea la sección de controles del radar responsiva."""
        self.frameControles = ctk.CTkFrame(self.principal)
        self.frameControles.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid
        self.frameControles.grid_columnconfigure(0, weight=1)
        self.frameControles.grid_columnconfigure(1, weight=1)
        self.frameControles.grid_columnconfigure(2, weight=1)
        
        # ========== OPERACIÓN ==========
        self._create_operation_controls()
        
        # ========== SLIDERS (Inclinación y Ganancia) ==========
        self._create_slider_controls()
        
        # ========== BOTONES DE RANGO Y TRACK ==========
        self._create_range_track_controls()
    
    def _create_operation_controls(self):
        """Crea controles de operación."""
        self.frameOperacion = ctk.CTkFrame(self.frameControles)
        self.frameOperacion.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Título
        header = ctk.CTkFrame(self.frameOperacion, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, pady=(5, 15), sticky="ew")
        
        ctk.CTkLabel(
            header,
            text='Operación:',
            font=('Arial', 14, 'bold')
        ).pack(side="left", padx=(10, 5))
        
        self.labelEncendido = ctk.CTkLabel(
            header,
            text='OFF',
            text_color='red',
            font=('Arial', 14, 'bold')
        )
        self.labelEncendido.pack(side="left")
        
        # Botones en grid 2x2 con paleta profesional
        self.botonOFF = ctk.CTkButton(
            self.frameOperacion,
            text='⭘ Apagar',
            font=('Arial', 12, 'bold'),
            fg_color='#dc2626',  # Rojo sobrio - Crítico
            hover_color='#991b1b',
            height=45,
            command=self.apagarRadar,
            state='disabled'
        )
        self.botonOFF.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.botonStandby = ctk.CTkButton(
            self.frameOperacion,
            text='⏸ Standby',
            font=('Arial', 12, 'bold'),
            fg_color='#2563eb',  # Azul profesional - Pausa
            hover_color='#1e40af',
            height=45,
            command=self.modoStandby,
            state='disabled'
        )
        self.botonStandby.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.botonTEST = ctk.CTkButton(
            self.frameOperacion,
            text='⚠ TEST',
            font=('Arial', 12, 'bold'),
            fg_color='#ea580c',  # Naranja sobrio - Advertencia
            hover_color='#c2410c',
            height=45,
            command=self.modoTEST,
            state='disabled'
        )
        self.botonTEST.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.botonON = ctk.CTkButton(
            self.frameOperacion,
            text='✓ ON',
            font=('Arial', 12, 'bold'),
            fg_color='#16a34a',  # Verde profesional - Activo
            hover_color='#15803d',
            height=45,
            command=self.modoON,
            state='disabled'
        )
        self.botonON.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Configurar columnas
        self.frameOperacion.grid_columnconfigure(0, weight=1)
        self.frameOperacion.grid_columnconfigure(1, weight=1)
    
    def _create_slider_controls(self):
        """Crea controles de sliders."""
        self.frameSliders = ctk.CTkFrame(self.frameControles)
        self.frameSliders.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid
        self.frameSliders.grid_columnconfigure(0, weight=1)
        self.frameSliders.grid_columnconfigure(1, weight=1)
        
        # Inclinación
        ctk.CTkLabel(
            self.frameSliders,
            text='Inclinación',
            font=('Arial', 13, 'bold')
        ).grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.sliderInclinacion = ctk.CTkSlider(
            self.frameSliders,
            from_=-15, to=15,
            orientation="horizontal",
            state="disabled",
            command=self.actualizar_inclinacion
        )
        self.sliderInclinacion.set(0)
        self.sliderInclinacion.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.entryInclinacion = ctk.CTkEntry(
            self.frameSliders,
            width=70,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entryInclinacion.grid(row=2, column=0, padx=10, pady=5)
        
        # Ganancia
        ctk.CTkLabel(
            self.frameSliders,
            text='Ganancia',
            font=('Arial', 13, 'bold')
        ).grid(row=0, column=1, padx=10, pady=(10, 5))
        
        self.sliderGain = ctk.CTkSlider(
            self.frameSliders,
            from_=-31.5, to=0,
            orientation="horizontal",
            state="disabled",
            command=self.proximo_gain
        )
        self.sliderGain.set(0)
        self.sliderGain.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.sliderGain.bind("<ButtonRelease-1>", self.actualizar_gain)
        
        self.entryGain = ctk.CTkEntry(
            self.frameSliders,
            width=70,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entryGain.grid(row=2, column=1, padx=10, pady=5)
    
    def _create_range_track_controls(self):
        """Crea controles de rango y track."""
        self.frameBotones = ctk.CTkFrame(self.frameControles)
        self.frameBotones.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid
        self.frameBotones.grid_columnconfigure(0, weight=1)
        self.frameBotones.grid_columnconfigure(1, weight=1)
        self.frameBotones.grid_columnconfigure(2, weight=1)
        
        # Rango (RNG) - Tono ámbar profesional
        self.botonRNGarriba = ctk.CTkButton(
            self.frameBotones,
            text='RNG ▲',
            font=('Arial', 12, 'bold'),
            fg_color='#ca8a04',  # Ámbar oscuro - Ajuste de escala
            hover_color='#a16207',
            text_color='white',  # Texto blanco para mejor contraste
            height=40,
            command=self.rangoArriba,
            state='disabled'
        )
        self.botonRNGarriba.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.entryRNG = ctk.CTkEntry(
            self.frameBotones,
            width=70,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entryRNG.grid(row=1, column=0, rowspan=2, padx=5, pady=5)
        
        self.botonRNGabajo = ctk.CTkButton(
            self.frameBotones,
            text='RNG ▼',
            font=('Arial', 12, 'bold'),
            fg_color='#ca8a04',  # Ámbar oscuro - Ajuste de escala
            hover_color='#a16207',
            text_color='white',  # Texto blanco para mejor contraste
            height=40,
            command=self.rangoAbajo,
            state='disabled'
        )
        self.botonRNGabajo.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Perfil Vertical (VP) - Púrpura para función especial
        self.botonVp = ctk.CTkButton(
            self.frameBotones,
            text='VP',
            font=('Arial', 12, 'bold'),
            fg_color='#7c3aed',  # Púrpura profesional - Función especial
            hover_color='#6d28d9',
            height=90,
            command=self.perfilVertical,
            state='disabled'
        )
        self.botonVp.grid(row=0, column=1, rowspan=4, padx=5, pady=5, sticky="nsew")
        
        # Track (TRK) - Azul cian para navegación
        self.botonTRKizquierda = ctk.CTkButton(
            self.frameBotones,
            text='TRK ◄',
            font=('Arial', 12, 'bold'),
            fg_color='#0891b2',  # Cian profesional - Navegación
            hover_color='#0e7490',
            height=40,
            command=self.trakerIzquierda,
            state='disabled'
        )
        self.botonTRKizquierda.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.entryTrack = ctk.CTkEntry(
            self.frameBotones,
            width=70,
            font=('Arial', 12, 'bold'),
            state='disabled',
            justify='center'
        )
        self.entryTrack.grid(row=1, column=2, rowspan=2, padx=5, pady=5)
        
        self.botonTRKderecha = ctk.CTkButton(
            self.frameBotones,
            text='TRK ►',
            font=('Arial', 12, 'bold'),
            fg_color='#0891b2',  # Cian profesional - Navegación
            hover_color='#0e7490',
            height=40,
            command=self.trakerDerecha,
            state='disabled'
        )
        self.botonTRKderecha.grid(row=3, column=2, padx=5, pady=5, sticky="ew")
    
    # ==================== MÉTODOS DE LA CLASE ====================
    # (Copio los métodos existentes del código legacy)
    
    def actualizar_puertos(self):
        """Actualiza lista de puertos disponibles."""
        self.combobox_port.configure(state='normal')
        self.datos_arduino.puertos_disponibles()
        self.port = self.datos_arduino.puertos
        self.combobox_port.configure(values=self.port)
        self.combobox_port.set(self.port[0] if self.port else "")
        self.combobox_port.configure(state='readonly')
    
    def conectar_serial(self):
        """Conecta al puerto serial."""
        self.datos_arduino.arduino.port = self.combobox_port.get()
        self.datos_arduino.arduino.baudrate = self.combobox_baud.get()
        self.datos_arduino.conexion_serial()
        
        import time
        time.sleep(0.5)
        self.datos_arduino.arduino.reset_input_buffer()
        
        if self.datos_arduino.status:
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
            
            self.label_estado.configure(text="● Conectado", text_color="lightgreen")
            messagebox.showinfo("Conexión", "Conectado al puerto serial.")
    
    def desconectar_serial(self):
        """Desconecta del puerto serial."""
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
        self.flagsliders2 = 0
        
        self.label_estado.configure(text="● Desconectado", text_color="red")
        messagebox.showinfo("Desconexión", "Desconectado del puerto serial.")
    
    # ... (Resto de métodos del código original)
    # Los métodos de control (modoStandby, modoTEST, etc.) se copian tal cual
    
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
            else:
                self.datos_arduino.enviar_datos("TU" + str(abs(dato)))
    
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
            self.botonVp.configure(fg_color='#16a34a', hover_color='#15803d')  # Verde cuando activo
        else:
            self.perfil = 0
            self.botonVp.configure(fg_color='#7c3aed', hover_color='#6d28d9')  # Púrpura cuando inactivo
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
            
            try:
                # Guardar ángulos de vista
                elev = self.ax.elev
                azim = self.ax.azim
                
                # CORRECCIÓN: Destruir el canvas anterior antes de crear uno nuevo
                if hasattr(self.frameGG, 'canvas'):
                    self.frameGG.canvas.get_tk_widget().destroy()
                
                # Cerrar la figura anterior
                plt.close(self.fig)
                
                # Crear nueva figura con el robot actualizado
                self.robot.plot([np.deg2rad(dato1num), np.deg2rad(dato2num)],
                              limits=[-0.5, 0.5, -0.5, 0.5, 0, 0.8])
                self.fig = plt.gcf()
                self.ax = plt.gca()
                
                # Crear nuevo canvas
                self.frameGG.canvas = FigureCanvasTkAgg(self.fig, master=self.frameGG)
                self.ax.plot([0, 1], [0, 0], [0, 0])
                self.ax.view_init(elev=elev, azim=azim)
                
                # Empaquetar el nuevo canvas
                self.frameGG.canvas.get_tk_widget().pack(fill="both", expand=True)
                self.frameGG.canvas.draw()
            except Exception as e:
                logger.error(f"Error al actualizar robot: {e}")


# Alias para compatibilidad
panel_control = ResponsiveControlPanel

