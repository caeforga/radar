# 🗺️ Panel de Mapa Geográfico - Software Radar

## 📋 **Descripción**

El Panel de Mapa es un nuevo componente del Software Radar que muestra una vista geográfica interactiva con la ubicación del radar superpuesta sobre un mapa satelital o de calles.

**Características principales:**
- ✅ Mapa interactivo que ocupa todo el panel
- ✅ Datos del radar mostrados como overlays sobre el mapa
- ✅ Actualización automática de posición GPS
- ✅ Círculos de rango visual
- ✅ Sector de cobertura del radar
- ✅ Leyenda de colores dBZ
- ✅ Soporte para múltiples tipos de mapa

---

## 🎨 **Vista del Panel**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌─────────────────┐                    ┌─────────────────────┐│
│  │📍 UBICACIÓN     │                    │📊 PARÁMETROS        ││
│  │Lat: -34.60370°  │                    │📏 Rango: 80 km      ││
│  │Lon: -58.38160°  │                    │📶 Ganancia: 0 dB    ││
│  │🧭 Orient: 45°   │                    │▶ ON                 ││
│  └─────────────────┘                    └─────────────────────┘│
│                                                                 │
│                    ╔═══════════════════╗                       │
│                    ║                   ║         ┌──────────┐  │
│                    ║   MAPA SATÉLITE   ║         │   dBZ    │  │
│                    ║   CON OVERLAY     ║         │ ▓ 58+    │  │
│                    ║   DEL RADAR       ║         │ ▓ 54     │  │
│                    ║                   ║         │ ▓ 50     │  │
│                    ║  ┌─────────────┐  ║         │ ▓ 46     │  │
│                    ║  │  📡 RADAR   │  ║         │ ▓ 42     │  │
│                    ║  │  ◜     ◝    │  ║         │ ▓ 38     │  │
│                    ║  │      ●      │  ║         │ ▓ 34     │  │
│                    ║  │  ◟     ◞    │  ║         │ ▓ 30     │  │
│                    ║  └─────────────┘  ║         │ ▓ 26     │  │
│                    ║                   ║         │ ▓ 22     │  │
│                    ╚═══════════════════╝         │ ▓ 18     │  │
│                                                  │ ▓ 14     │  │
│  ┌─────────────────┐   ┌───────────────┐         │ ▓ 10     │  │
│  │● Sin Aceptación │   │ ──── 25 km ───│         └──────────┘  │
│  └─────────────────┘   └───────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 **Archivos**

### **Archivo Principal**
- `src/ui/panels/map_panel_responsive.py` - Implementación del panel

### **Archivos Modificados**
- `src/ui/panels/__init__.py` - Exportación del nuevo panel
- `src/ui/app_responsive.py` - Integración con la aplicación
- `requirements.txt` - Nueva dependencia `tkintermapview`

---

## 🛠️ **Tecnología Utilizada**

### **TkinterMapView**

```python
pip install tkintermapview
```

**Características:**
- ✅ Integración nativa con CustomTkinter
- ✅ Tiles de OpenStreetMap y Google Maps
- ✅ Sin necesidad de API key para uso básico
- ✅ Soporte para markers, polígonos y círculos
- ✅ Zoom y pan interactivo
- ✅ Múltiples servidores de tiles

---

## 📊 **Datos Mostrados**

### **Overlay Superior Izquierdo - Ubicación**
| Campo | Descripción | Formato |
|-------|-------------|---------|
| Latitud | Coordenada GPS N/S | `Lat: -34.60370°` |
| Longitud | Coordenada GPS E/O | `Lon: -58.38160°` |
| Orientación | Dirección de la brújula | `🧭 Orientación: 45°` |

### **Overlay Superior Derecho - Parámetros**
| Campo | Descripción | Formato |
|-------|-------------|---------|
| Rango | Alcance del radar | `📏 Rango: 80 km` |
| Ganancia | Nivel de ganancia | `📶 Ganancia: 0 dB` |
| Operación | Estado del radar | `▶ ON` / `⏸ STDBY` / `⚠ TEST` |

### **Overlay Inferior Izquierdo - Estado**
| Campo | Descripción | Colores |
|-------|-------------|---------|
| Aceptación | Estado de comunicación | 🟢 Aceptado / 🔴 Sin Aceptación |

### **Overlay Derecho - Escala dBZ**
| dBZ | Color | Significado |
|-----|-------|-------------|
| 58+ | Magenta | Granizo |
| 54 | Rojo | Tormenta severa |
| 50 | Rojo-naranja | Tormenta intensa |
| 46 | Naranja | Lluvia intensa |
| 42 | Amarillo | Lluvia moderada |
| 38 | Amarillo claro | Lluvia ligera |
| 34 | Verde | Lluvia débil |
| 30 | Verde medio | Llovizna |
| 26 | Verde oscuro | Precipitación ligera |
| 22 | Cyan | Humedad |
| 18 | Azul claro | Trazas |
| 14 | Azul | Señal débil |
| 10 | Azul oscuro | Ruido |

---

## 🗺️ **Elementos del Mapa**

### **1. Marker del Radar**
```python
self.radar_marker = self.map_widget.set_marker(
    self.latitud,
    self.longitud,
    text="📡 RADAR",
    marker_color_circle="#3b82f6",
    marker_color_outside="#1e40af"
)
```

### **2. Círculos de Rango**
Círculos concéntricos a 25, 50, 75 km y el rango configurado:
```python
distances = [25, 50, 75, self.rango]  # km
```

### **3. Sector de Cobertura**
Polígono que muestra el área de cobertura del radar (90° de apertura):
```python
apertura = 90  # grados
inicio = self.orientacion - apertura / 2
fin = self.orientacion + apertura / 2
```

---

## 🔄 **Ciclo de Actualización**

```python
def iniciar(self):
    """Inicia el ciclo de actualización automática."""
    if self._update_running:
        return
    self._update_running = True
    self._update_id = self.root.after(2000, self.actualizar)  # Cada 2 segundos

def actualizar(self):
    """Actualiza todos los componentes del panel."""
    # 1. Leer datos GPS y brújula
    # 2. Actualizar barrido del radar
    # 3. Actualizar overlays de información
    # 4. Actualizar elementos del mapa (marker, círculos, sector)
    # 5. Programar próxima actualización

def detener(self):
    """Detiene el ciclo de actualización."""
    self._update_running = False
    if self._update_id:
        self.root.after_cancel(self._update_id)
```

---

## 🎨 **Servidores de Tiles**

El panel soporta múltiples tipos de mapa:

```python
def set_tile_server(self, server_type="satellite"):
    servers = {
        "satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
        "street": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
        "terrain": "https://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}&s=Ga",
        "hybrid": "https://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga",
        "osm": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
    }
```

| Tipo | Descripción |
|------|-------------|
| `satellite` | Vista satelital de Google |
| `street` | Mapa de calles de Google |
| `terrain` | Mapa de terreno de Google |
| `hybrid` | Satélite + etiquetas |
| `osm` | OpenStreetMap |

---

## 🧮 **Cálculos Geográficos**

### **Cálculo de Puntos de Destino**

Para dibujar círculos y sectores, se usa la fórmula de navegación:

```python
def _calculate_destination(self, lat, lon, distance_km, bearing):
    """
    Calcula coordenadas de destino dado un punto, distancia y dirección.
    
    Fórmula de Haversine inversa:
    - lat2 = asin(sin(lat1)*cos(d/R) + cos(lat1)*sin(d/R)*cos(bearing))
    - lon2 = lon1 + atan2(sin(bearing)*sin(d/R)*cos(lat1), 
                          cos(d/R) - sin(lat1)*sin(lat2))
    """
    R = 6371  # Radio de la Tierra en km
    # ... cálculos ...
    return lat2, lon2
```

---

## 🔧 **Integración con la Aplicación**

### **En `app_responsive.py`**

```python
# Variable de estado
self.objeto_mapa = None

# Botón en el sidebar
self.btn_mapa = ctk.CTkButton(
    self.menu,
    text="  🗺️ Mapa",
    command=self.show_map_panel
)

# Método para mostrar el panel
def show_map_panel(self):
    # Verificar conexión serial
    # Detener otros paneles
    # Crear/mostrar panel de mapa
    # Iniciar actualización
```

### **Gestión de Ciclos**

Al cambiar de panel, se detienen los ciclos de actualización de los otros paneles:

```python
# En show_control_panel():
if self.objeto_mapa is not None:
    self.objeto_mapa.detener()

# En show_visualization_panel():
if self.objeto_mapa is not None:
    self.objeto_mapa.detener()

# En show_map_panel():
if self.objeto_visualizacion is not None:
    self.objeto_visualizacion.detener()
```

---

## 🧪 **Pruebas**

### **Test 1: Visualización del Mapa**
1. Conectar al puerto serial
2. Ir al panel de Mapa
3. **Verificar:**
   - ✅ Mapa se muestra correctamente
   - ✅ Overlays visibles
   - ✅ Zoom y pan funcionan

### **Test 2: Actualización de Datos**
1. Con GPS conectado
2. Observar cambios de posición
3. **Verificar:**
   - ✅ Marker se mueve con GPS
   - ✅ Círculos se actualizan
   - ✅ Sector sigue la orientación

### **Test 3: Cambio de Paneles**
1. Alternar entre Mapa ↔ Visualización ↔ Control
2. **Verificar:**
   - ✅ Sin duplicación
   - ✅ Ciclos se detienen/inician correctamente
   - ✅ Sin errores

---

## 📝 **Uso**

```bash
# 1. Instalar dependencia
pip install tkintermapview

# 2. Ejecutar aplicación
python run.py

# 3. Conectar al puerto serial (desde panel Control)

# 4. Ir al panel de Mapa (botón 🗺️ Mapa)
```

---

## 🔮 **Mejoras Futuras**

### **1. Overlay de Reflectividad**
Superponer los datos de reflectividad (dBZ) como una capa semitransparente sobre el mapa.

### **2. Selector de Tipo de Mapa**
Agregar un dropdown para cambiar entre satélite, calles, terreno, etc.

### **3. Historial de Posiciones**
Mostrar la trayectoria del radar si está en movimiento.

### **4. Puntos de Interés**
Agregar markers para ciudades, aeropuertos u otros puntos relevantes.

### **5. Medición de Distancias**
Herramienta para medir distancias entre puntos en el mapa.

---

## ✅ **Estado**

| Característica | Estado |
|----------------|--------|
| **Mapa interactivo** | ✅ Implementado |
| **Overlays de información** | ✅ Implementado |
| **Marker del radar** | ✅ Implementado |
| **Círculos de rango** | ✅ Implementado |
| **Sector de cobertura** | ✅ Implementado |
| **Leyenda dBZ** | ✅ Implementado |
| **Actualización automática** | ✅ Implementado |
| **Gestión de ciclos** | ✅ Implementado |
| **Sin errores de linting** | ✅ Verificado |

---

**Archivo:** `src/ui/panels/map_panel_responsive.py`  
**Dependencia:** `tkintermapview`  
**Estado:** ✅ **IMPLEMENTADO Y FUNCIONANDO**  
**Fecha:** Noviembre 2025

---

## 🚀 **¡Listo para Usar!**

```bash
python run.py
```

El nuevo panel de Mapa está disponible en el menú lateral con el botón 🗺️ **Mapa**.

¡Disfruta de la nueva vista geográfica del radar! 🎉

