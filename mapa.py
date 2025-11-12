import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import gaussian_filter

# Crear figura
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# Simular datos de elevación (en la práctica, usa datos reales como SRTM)
lat = np.linspace(-90, 90, 100)
lon = np.linspace(-180, 180, 100)
lon_grid, lat_grid = np.meshgrid(lon, lat)
elevation = np.sin(np.radians(lat_grid * 2)) * np.cos(np.radians(lon_grid / 2)) * 5000  # Datos sintéticos

# Aplicar filtro Gaussiano para suavizar
elevation_smooth = gaussian_filter(elevation, sigma=2)

# Añadir sombreado (hillshading)
ls = plt.LightSource(azdeg=315, altdeg=45)  # Ángulo de iluminación
rgb = ls.shade(elevation_smooth, cmap=plt.cm.terrain, vert_exag=100, blend_mode='soft')

# Mostrar el relieve
ax.imshow(rgb, extent=[-180, 180, -90, 90], transform=ccrs.PlateCarree(), alpha=0.7)

# Añadir características geográficas
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)

plt.title("Relieve con Hillshading (Cartopy + Matplotlib)")
plt.show()