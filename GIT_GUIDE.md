# 📚 Guía de Git para Software Radar

Esta guía te ayudará a usar Git correctamente con este proyecto.

---

## 🚀 Configuración Inicial

### 1. Inicializar el repositorio (si aún no está inicializado)

```bash
git init
```

### 2. Configurar tu identidad (primera vez)

```bash
git config user.name "Tu Nombre"
git config user.email "tuemail@ejemplo.com"
```

### 3. Verificar archivos ignorados

```bash
# Ver qué archivos serán ignorados
git status --ignored
```

---

## 📝 Archivos de Configuración de Git

### `.gitignore`
Define qué archivos y carpetas NO se versionan:
- ✅ **Entorno virtual** (`venv/`)
- ✅ **Archivos compilados** (`__pycache__/`, `*.pyc`)
- ✅ **Datos generados** (`output/`, `*.png`, `*.csv`)
- ✅ **Configuraciones locales** (`.env`, `config.ini`)
- ✅ **Archivos del IDE** (`.vscode/`, `.idea/`)

### `.gitattributes`
Define cómo Git maneja diferentes tipos de archivos:
- 📄 **Normaliza line endings** (LF para Unix, CRLF para Windows)
- 🔢 **Marca archivos binarios** (imágenes, PDFs, archivos comprimidos)
- 📦 **Excluye archivos del export** (archivos de desarrollo)

### `.gitkeep`
Mantiene carpetas vacías en el repositorio:
- `output/Lecturas RADAR/.gitkeep`
- `output/RawData/.gitkeep`

---

## 🔄 Flujo de Trabajo Básico

### 1. Ver el estado actual

```bash
git status
```

### 2. Añadir archivos al staging

```bash
# Añadir archivo específico
git add mejorada.py

# Añadir múltiples archivos
git add ComSerial.py GPS.py

# Añadir todos los archivos modificados
git add .
```

### 3. Hacer commit

```bash
git commit -m "Descripción clara de los cambios"
```

**Ejemplos de buenos mensajes:**
```bash
git commit -m "feat: Añadir soporte para perfil vertical"
git commit -m "fix: Corregir error en lectura GPS"
git commit -m "docs: Actualizar README con instrucciones de instalación"
git commit -m "refactor: Mejorar estructura del panel de control"
```

### 4. Ver historial

```bash
# Ver commits recientes
git log --oneline

# Ver cambios detallados
git log -p
```

---

## 🌿 Trabajo con Ramas

### Crear una nueva rama

```bash
# Crear y cambiar a nueva rama
git checkout -b feature/nueva-funcionalidad

# O en Git moderno
git switch -c feature/nueva-funcionalidad
```

### Cambiar entre ramas

```bash
git checkout main
git checkout feature/nueva-funcionalidad

# O en Git moderno
git switch main
git switch feature/nueva-funcionalidad
```

### Ver ramas

```bash
# Ver ramas locales
git branch

# Ver todas las ramas (incluyendo remotas)
git branch -a
```

### Fusionar ramas

```bash
# Cambia a la rama destino
git checkout main

# Fusiona la rama
git merge feature/nueva-funcionalidad
```

### Eliminar rama

```bash
# Eliminar rama local
git branch -d feature/nueva-funcionalidad

# Forzar eliminación
git branch -D feature/nueva-funcionalidad
```

---

## 🌐 Trabajo con Repositorio Remoto

### Añadir repositorio remoto

```bash
git remote add origin https://github.com/tuusuario/SoftwareRadar.git
```

### Ver repositorios remotos

```bash
git remote -v
```

### Subir cambios (Push)

```bash
# Primera vez (establece upstream)
git push -u origin main

# Subsecuentes pushes
git push
```

### Descargar cambios (Pull)

```bash
git pull origin main
```

### Clonar repositorio

```bash
git clone https://github.com/tuusuario/SoftwareRadar.git
cd SoftwareRadar
```

---

## 🔧 Comandos Útiles

### Ver diferencias

```bash
# Ver cambios no staged
git diff

# Ver cambios staged
git diff --staged

# Comparar con commit anterior
git diff HEAD~1
```

### Deshacer cambios

```bash
# Descartar cambios en archivo (¡cuidado!)
git checkout -- archivo.py

# Quitar archivo del staging (mantiene cambios)
git reset HEAD archivo.py

# Deshacer último commit (mantiene cambios)
git reset --soft HEAD~1

# Deshacer último commit (descarta cambios, ¡cuidado!)
git reset --hard HEAD~1
```

### Ver archivos ignorados

```bash
# Listar archivos ignorados
git status --ignored

# Ver por qué un archivo está ignorado
git check-ignore -v archivo.py
```

### Limpiar archivos no rastreados

```bash
# Ver qué se eliminará (simulación)
git clean -n

# Eliminar archivos no rastreados
git clean -f

# Eliminar archivos y carpetas
git clean -fd
```

---

## 📦 Preparar para Primera Subida

### Paso a paso completo

```bash
# 1. Inicializar repositorio (si no está hecho)
git init

# 2. Añadir todos los archivos
git add .

# 3. Verificar qué se añadirá
git status

# 4. Hacer primer commit
git commit -m "Initial commit: Software Radar v1.0"

# 5. Añadir repositorio remoto
git remote add origin https://github.com/tuusuario/SoftwareRadar.git

# 6. Subir cambios
git push -u origin main
```

---

## ⚠️ Archivos que NO se deben versionar

Los siguientes archivos están en `.gitignore` y NO deben subirse:

### ❌ Nunca subir:
- `venv/` - Entorno virtual (se reinstala con `pip install -r requirements.txt`)
- `.env` - Variables de entorno con datos sensibles
- `__pycache__/` - Archivos compilados de Python
- `*.pyc` - Bytecode de Python
- `.vscode/`, `.idea/` - Configuraciones del IDE (personales)
- `output/` - Datos generados por la aplicación

### ✅ Sí versionar:
- `*.py` - Todo el código fuente
- `requirements.txt` - Dependencias del proyecto
- `README.md` - Documentación
- `imagenes/` - Recursos gráficos de la interfaz
- `FirmwareESP32/` - Código del firmware
- `PCB FINAL/` - Diseños de hardware (excepto backups)

---

## 🔐 Datos Sensibles

Si necesitas manejar datos sensibles (contraseñas, API keys):

### Usar variables de entorno

1. Crea un archivo `.env` (ya está en `.gitignore`):
```env
DATABASE_PASSWORD=tu_contraseña_secreta
API_KEY=tu_api_key
```

2. Crea un `.env.example` (este SÍ se versiona):
```env
DATABASE_PASSWORD=cambiar_por_tu_contraseña
API_KEY=cambiar_por_tu_api_key
```

3. En Python, carga con `python-dotenv`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv('DATABASE_PASSWORD')
```

---

## 🆘 Solución de Problemas

### "El archivo es demasiado grande"

Si tienes archivos grandes (>50MB):

```bash
# Opción 1: Añadir a .gitignore
echo "archivo_grande.csv" >> .gitignore

# Opción 2: Usar Git LFS
git lfs install
git lfs track "*.csv"
git add .gitattributes
```

### "Conflicto al hacer merge"

```bash
# 1. Ver archivos en conflicto
git status

# 2. Editar manualmente los archivos
# Busca las marcas: <<<<<<<, =======, >>>>>>>

# 3. Marcar como resuelto
git add archivo_resuelto.py

# 4. Completar el merge
git commit
```

### "Subí archivos que no debería"

```bash
# Eliminar del repositorio pero mantener localmente
git rm --cached archivo_sensible.py
git commit -m "Remove sensitive file"
git push

# Añadir a .gitignore
echo "archivo_sensible.py" >> .gitignore
```

---

## 📋 Checklist Antes de Cada Push

- [ ] He revisado los cambios con `git status`
- [ ] Los commits tienen mensajes descriptivos
- [ ] No estoy subiendo archivos sensibles (`.env`, contraseñas)
- [ ] No estoy subiendo archivos grandes innecesarios
- [ ] He probado el código localmente
- [ ] He actualizado la documentación si es necesario
- [ ] Los tests pasan (si los hay)

---

## 📚 Recursos Adicionales

- [Pro Git Book (Español)](https://git-scm.com/book/es/v2)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**¡Feliz versionado!** 🎉

