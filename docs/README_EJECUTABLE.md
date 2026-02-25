# 🚀 Software Radar - Guía de Uso del Ejecutable

## 📦 ¿Qué es esto?

**Software Radar** es una aplicación de visualización y control para sistemas de radar meteorológico. Este ejecutable te permite usar la aplicación sin necesidad de instalar Python ni ninguna dependencia adicional.

---

## 💻 Requisitos del Sistema

### **Mínimos:**
- 🖥️ Windows 10/11 (64-bit)
- 💾 RAM: 4 GB
- 💿 Espacio en disco: 500 MB libres
- 🔌 Puerto COM disponible (para conectar hardware)

### **Recomendados:**
- 💾 RAM: 8 GB o más
- 🖥️ Resolución: 1920x1080 o superior
- 🔌 Driver USB-to-Serial instalado (si usas adaptador USB)

---

## 🎯 Instalación

### **¡No requiere instalación!**

1. **Descarga el archivo:**
   - `SoftwareRadar.exe` (150-300 MB)

2. **Opcionalmente, crea una carpeta:**
   ```
   C:\Radar\
   └── SoftwareRadar.exe
   ```

3. **¡Listo para usar!**
   - Doble clic en `SoftwareRadar.exe`

---

## 🚀 Primera Ejecución

### **1. Al abrir la aplicación:**

Te aparecerá la pantalla de bienvenida con el menú lateral:
- 🎮 **Control** - Para conectar y controlar el radar
- 📊 **Visualización** - Para ver los datos del radar
- 🗺️ **Mapa** - Para visualización geográfica

### **2. Conectar el Hardware:**

1. **Conecta tu dispositivo** al puerto COM (USB/Serial)
2. Ve al panel **Control**
3. Selecciona el **puerto COM** de la lista
4. Selecciona la **velocidad** (9600 por defecto)
5. Click en **🔌 Conectar**

### **3. Empezar a usar:**

Una vez conectado:
- ✅ Los sliders se activan
- ✅ Puedes controlar el robot 3D
- ✅ Los modos de operación están disponibles

---

## 🎮 Guía Rápida de Uso

### **Panel de Control:**

#### **Conexión Serial:**
- **Puerto COM**: Selecciona el puerto donde está conectado tu dispositivo
- **Baud Rate**: Velocidad de comunicación (9600 típico)
- **Conectar**: Establece la conexión
- **Actualizar**: Refresca la lista de puertos

#### **Control del Robot:**
- **Slider Horizontal**: Motor de rotación (-180° a +180°)
- **Slider Vertical**: Motor de inclinación (-60° a +60°)
- Visualización en 3D en tiempo real

#### **Modos de Operación:**
- 🟥 **Apagar**: Apaga el radar
- 🔵 **Standby**: Modo de espera
- 🟧 **TEST**: Modo de prueba
- 🟩 **ON**: Operación normal

#### **Controles Avanzados:**
- **Inclinación**: Ajuste fino de ángulo
- **Ganancia**: Control de sensibilidad
- **RNG**: Cambiar rango de detección
- **VP**: Perfil vertical
- **TRK**: Tracking de objetivos

---

### **Panel de Visualización:**

#### **Gráfico del Radar:**
- Visualización en tiempo real de detecciones
- Colores indican intensidad
- Actualización automática cada segundo

#### **Indicadores:**
- **Aceptación**: Estado de la señal
- **Operación**: Modo actual (STDBY/TEST/ON)
- **Fallos**: Lista de errores detectados
- **Modo especial**: Características activas

#### **Parámetros:**
- **Rango**: Distancia de detección
- **Ganancia**: Nivel de amplificación
- **Inclinación**: Ángulo del radar
- **Track**: Seguimiento activo

#### **Sensores Meteorológicos:**
- 🌡️ Temperatura
- 💧 Humedad
- 📊 Presión atmosférica
- 🌬️ Velocidad del viento
- 🧭 Dirección del viento
- 🌧️ Precipitación

#### **GPS y Brújula:**
- 📍 Coordenadas GPS en tiempo real
- 🧭 Orientación de la antena

---

## ⚠️ Solución de Problemas

### **El ejecutable no abre:**

1. **Antivirus bloqueando:**
   - Algunos antivirus marcan ejecutables desconocidos
   - Agregar excepción para `SoftwareRadar.exe`
   - Es seguro, el código es de fuente abierta

2. **Falta Visual C++ Runtime:**
   - Descargar e instalar [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

3. **Windows SmartScreen:**
   - Click en "Más información"
   - Click en "Ejecutar de todas formas"

---

### **No aparecen puertos COM:**

1. **Verifica la conexión:**
   - Cable USB conectado correctamente
   - LED del dispositivo encendido

2. **Instala drivers:**
   - Si usas adaptador USB-to-Serial, instala sus drivers
   - Común: CH340, CP2102, FTDI

3. **Verifica en Administrador de Dispositivos:**
   - Windows + X → Administrador de dispositivos
   - Busca en "Puertos (COM y LPT)"
   - Anota el número de COM (ej: COM3)

4. **Click en "Actualizar":**
   - Botón 🔄 Actualizar Puertos en la aplicación

---

### **Error al conectar:**

1. **Puerto ya en uso:**
   - Cierra otros programas que usen el puerto
   - Arduino IDE, Putty, otras aplicaciones serial

2. **Velocidad incorrecta:**
   - Prueba con 9600, 115200, u otras velocidades
   - Debe coincidir con la configuración del firmware

3. **Reinicia el dispositivo:**
   - Desconecta y reconecta el cable USB
   - Click en Actualizar

---

### **Robot 3D no se muestra:**

- Requiere bibliotecas de visualización 3D
- Puede tardar en cargar la primera vez
- Si no aparece, la funcionalidad sigue disponible

---

### **La aplicación se congela:**

1. **Memoria insuficiente:**
   - Cierra otros programas
   - Requiere mínimo 4 GB RAM

2. **Comunicación perdida:**
   - Desconectar y reconectar
   - Revisar cable/conexión

---

### **Datos no se actualizan:**

1. **Verificar conexión activa:**
   - Indicador debe mostrar "● Conectado" en verde

2. **Firmware del dispositivo:**
   - Asegúrate que el firmware está enviando datos correctamente

3. **Reiniciar la aplicación:**
   - Cerrar y volver a abrir

---

## 🔒 Seguridad y Privacidad

- ✅ **No requiere internet** (funciona offline)
- ✅ **No recopila datos** del usuario
- ✅ **No envía información** a servidores externos
- ✅ **Solo accede** al puerto serial seleccionado
- ✅ **Código abierto** disponible en GitHub

---

## 📊 Archivos de Datos

### **Archivos CSV de Sensores:**

Si tienes archivos de datos meteorológicos:

```
C:\Radar\
├── SoftwareRadar.exe
└── CR310_RK900_10.csv          # Datos del sensor
```

La aplicación buscará automáticamente este archivo en el mismo directorio.

---

## 🎨 Personalización

### **Resolución de Pantalla:**

La interfaz es **completamente responsiva**:
- ✅ Se adapta automáticamente a tu pantalla
- ✅ Funciona desde 1024x600 hasta 4K
- ✅ Redimensiona la ventana libremente

### **Temas:**

Actualmente usa tema oscuro optimizado para:
- 👁️ Reducir fatiga visual
- 🌙 Trabajo nocturno
- 💡 Mejor contraste para datos

---

## 📝 Atajos de Teclado

_Próximamente_

---

## 🔄 Actualización

Para actualizar a una nueva versión:

1. **Descarga** el nuevo `SoftwareRadar.exe`
2. **Reemplaza** el archivo anterior
3. **¡Listo!** Mantiene toda tu configuración

---

## 📞 Soporte Técnico

### **Contacto:**
- 📧 Email: [tu-email@ejemplo.com]
- 💬 GitHub Issues: [link-al-repositorio]
- 📖 Documentación completa: [link-a-docs]

### **Información del Sistema:**

Para reportar problemas, incluye:
- Versión de Windows
- Tamaño de pantalla/resolución
- Modelo del dispositivo conectado
- Screenshot del error (si aplica)

---

## 📚 Recursos Adicionales

- 📖 [Manual de Usuario Completo](MANUAL_USUARIO.md)
- 🎓 [Tutorial en Video](link-a-video)
- 🔧 [Guía de Hardware](HARDWARE_GUIDE.md)
- 💻 [Código Fuente](https://github.com/tu-repo)

---

## ⚖️ Licencia

Este software se distribuye bajo [LICENCIA].

---

## 🙏 Créditos

Desarrollado por [Tu Nombre/Organización]  
Basado en tecnología de radar meteorológico  
Interfaz responsiva con CustomTkinter  
Visualización 3D con Robotics Toolbox

---

## 🌟 Características

- ✨ Interfaz moderna y responsiva
- 🤖 Visualización 3D del robot en tiempo real
- 📊 Gráficos de radar actualizados automáticamente
- 🗺️ Integración con GPS y brújula
- 🌤️ Sensores meteorológicos
- 🎮 Control completo del hardware
- 📱 Funciona en múltiples resoluciones
- 🚀 Sin instalación requerida

---

**Versión:** 2.0  
**Fecha:** Noviembre 2025  
**Compatible con:** Windows 10/11 (64-bit)

¡Gracias por usar Software Radar! 🎉

