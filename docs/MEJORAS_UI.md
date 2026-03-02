# Mejoras y Correcciones - Software Radar v2.0

Este documento describe las mejoras realizadas y los errores corregidos respecto al software base original (`mejorada.py`).

---

## Reestructuración del Código

### Estructura anterior (v1.x)

```
SoftwareRadar/
├── mejorada.py          # Todo en un archivo (1192 líneas)
├── ComSerial.py
├── GPS.py
├── CargaSensor.py
├── Interpretacion.py
├── imagenes/
└── [15+ archivos en raíz]
```

### Estructura actual (v2.0)

```
SoftwareRadar/
├── src/
│   ├── config/settings.py               # Configuración centralizada
│   ├── core/
│   │   ├── communication/serial_comm.py  # SerialCommunication (antes ComSerial.py)
│   │   ├── hardware/gps.py              # GPSParser (antes GPS.py)
│   │   ├── hardware/sensor.py           # WeatherSensor (antes CargaSensor.py)
│   │   └── data/interpretation.py       # Interpretación de datos
│   ├── ui/
│   │   ├── app_responsive.py            # Aplicación principal responsiva
│   │   └── panels/
│   │       ├── control_panel_responsive.py
│   │       └── visualization_panel_responsive.py
│   └── main.py
├── assets/images/
├── run.py
└── requirements.txt
```

### Principales cambios en el código

| Aspecto | Antes (v1.x) | Ahora (v2.0) |
|---------|--------------|--------------|
| Archivos en raíz | 15+ | 2 (`run.py`, `README.md`) |
| Documentación de funciones | ~30% | 100% |
| Type hints | 0% | 90% |
| Configuración hardcoded | 100% | Centralizada en `Settings` |
| Logging | `print()` | `logging` estructurado |

---

## UI Responsiva

### Problema original

La UI base tenía tamaño fijo de 1200x800 píxeles, estaba optimizada solo para 1920x1080, y los elementos se rompían al redimensionar la ventana.

### Solución implementada

**Ventana adaptativa:**
- Tamaño automático (85% de la pantalla)
- Centrado automático en cualquier monitor
- Tamaño mínimo de 1000x600
- Redimensionable sin romper el diseño

**Sistema de grid responsivo:**
- Grid system con weights para distribución proporcional
- Eliminación de todos los tamaños fijos en píxeles
- Componentes con `sticky="nsew"` para expansión automática

**Menú lateral mejorado:**
- Botones con iconos y texto
- Indicador de conexión serial en tiempo real (verde/rojo)
- Retroalimentación visual del botón activo

**Logo y pantalla de bienvenida adaptativos:**
- Logo ocupa 50% del contenedor, mantiene proporciones
- Centrado perfecto vertical y horizontal

### Comparación

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Tamaño ventana | 1200x800 fijo | 85% de pantalla |
| Resoluciones | Solo 1920x1080 | Cualquiera |
| Redimensionar | Se rompe | Funciona perfecto |
| Espacio utilizado | ~60% | ~85-95% |
| Estado de conexión | No visible | Siempre visible |

### Resoluciones soportadas

Funciona correctamente en: 1280x720, 1366x768, 1600x900, 1920x1080, 2560x1440, 3840x2160.

---

## Paneles Responsivos

### Panel de Control

**Distribución con grid weights:**
- Row 0 (weight=2): Área superior — Robot 3D + Serial (60% del espacio)
- Row 1 (weight=1): Área inferior — Controles (40% del espacio)
- Column 0 (weight=3): Robot y sliders (75% del ancho)
- Column 1 (weight=1): Configuración serial (25% del ancho)

**Cambios principales:**
- Sliders que se expanden con la ventana (antes: ancho fijo de 750px)
- Robot 3D que se adapta al contenedor (antes: 400x400 fijo)
- Controles de operación en grid 2x2 con distribución equitativa

### Panel de Visualización

**Distribución 25-75:**
- Columna izquierda (weight=1): Panel de indicadores scrollable
- Columna derecha (weight=3): Gráfico del radar

**Cambios principales:**
- Canvas de Matplotlib con redimensionamiento dinámico vía callback `_on_canvas_resize`
- Panel de indicadores con scroll automático para pantallas pequeñas
- Gráfico del radar que ocupa todo el espacio disponible

### Fallback automático

Si los paneles responsivos fallan, la aplicación carga automáticamente la versión legacy (`mejorada.py`) sin intervención del usuario.

---

## Paleta de Colores

Se reemplazaron los colores básicos de HTML por una paleta profesional con significado funcional.

### Colores por función

| Función | Color | Código | Hover | Uso |
|---------|-------|--------|-------|-----|
| Crítico/Destructivo | Rojo | `#dc2626` | `#991b1b` | Apagar, Desconectar |
| Positivo/Activo | Verde | `#16a34a` | `#15803d` | Conectar, ON, VP activo |
| Pausa/Intermedio | Azul | `#2563eb` | `#1e40af` | Standby |
| Advertencia | Naranja | `#ea580c` | `#c2410c` | TEST |
| Ajuste de valores | Ámbar | `#ca8a04` | `#a16207` | RNG (texto blanco) |
| Navegación | Cian | `#0891b2` | `#0e7490` | TRK |
| Función especial | Púrpura | `#7c3aed` | `#6d28d9` | VP inactivo |
| Secundario | Gris | `#475569` | `#334155` | Actualizar puertos |

### Colores de la interfaz general

```
Menú lateral:      #1F6AA5 (Azul corporativo)
Botón activo:      #4A90D9 (Azul brillante)
Contenedor:        #242424 (Gris oscuro)
Texto principal:   #FFFFFF (Blanco)
Texto secundario:  #AAAAAA (Gris claro)
Estado OK:         #90EE90 (Verde claro)
Estado Error:      #FF6B6B (Rojo suave)
```

### Guía para nuevos botones

1. Identificar la función del botón (crítica, positiva, navegación, etc.)
2. Usar el color correspondiente de la tabla anterior
3. Siempre incluir `hover_color`
4. Usar `text_color='white'` sobre fondos oscuros

---

---

## Correcciones de Errores

### 1. Gráfico 3D duplicado (Panel de Control)

**Problema**: Al mover el slider de rotación, el gráfico 3D del robot se duplicaba y el panel de opciones inferior desaparecía. Cada movimiento del slider creaba un nuevo canvas de Matplotlib sin destruir el anterior, provocando acumulación de widgets.

**Solución**: Destruir el canvas anterior antes de crear uno nuevo:

```python
if hasattr(self.frameGG, 'canvas'):
    self.frameGG.canvas.get_tk_widget().destroy()
```

**Archivo**: `src/ui/panels/control_panel_responsive.py`

### 2. Ciclos de actualización duplicados (Panel de Visualización)

**Problema**: Al cambiar entre paneles, el ciclo de actualización automática (cada segundo) no se detenía. Cada vez que se volvía al panel de visualización se creaba un ciclo adicional, causando actualizaciones múltiples, vista duplicada y degradación progresiva del rendimiento.

**Solución**: Variables de control (`_update_running`, `_update_id`) para prevenir ciclos duplicados, método `detener()` que cancela el timer, y llamada a `detener()` al cambiar de panel.

**Archivos**: `src/ui/panels/visualization_panel_responsive.py`, `src/ui/app_responsive.py`

### 3. Sobreposición de indicadores sobre el gráfico (Panel de Visualización)

**Problema**: El panel de indicadores con ancho fijo de 250px se expandía sobre el gráfico del radar porque los grid weights proporcionales no funcionaban bien con un `CTkScrollableFrame` de ancho fijo.

**Solución**: Cambiar la columna de indicadores a `weight=0, minsize=280` (ancho fijo gestionado por el grid) y la columna del gráfico a `weight=1` (ocupa todo el espacio restante). Se eliminó el `width=250` del frame.

**Archivo**: `src/ui/panels/visualization_panel_responsive.py`

### 4. Duplicación del panel al cambiar entre vistas

**Problema**: Los paneles hacían `grid()` en su `__init__` y también desde `app_responsive.py`, resultando en posicionamiento duplicado y widgets superpuestos. Además, los widgets residuales no se limpiaban al cambiar de panel.

**Solución**: Los paneles ya no hacen `grid()` en su `__init__` (solo crean el frame). El posicionamiento se hace exclusivamente desde `app_responsive.py`, que además limpia todos los widgets del contenedor antes de mostrar un panel nuevo.

**Archivos**: `visualization_panel_responsive.py`, `control_panel_responsive.py`, `app_responsive.py`

### 5. Iconos no encontrados en el ejecutable compilado

**Problema**: Al compilar con PyInstaller, las imágenes no se encontraban porque `__file__` apunta a una ubicación temporal dentro del ejecutable empaquetado.

**Solución**: Función `get_resource_path()` que detecta si la aplicación está empaquetada y usa `sys._MEIPASS` en ese caso:

```python
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)
```

**Archivos**: `src/ui/app_responsive.py`, `mejorada.py`
