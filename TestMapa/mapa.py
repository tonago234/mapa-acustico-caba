import geopandas as gpd
import pandas as pd
import folium
import sys

print("Cargando el mapa de ruido 2018 desde el formato nativo...")

try:
    # 1. Leer el Shapefile nativo
    gdf_ruido = gpd.read_file("mapa_de_ruido_diurno.shp") 
    print(f"¡Archivo cargado! Total de filas originales: {len(gdf_ruido)}")
    
    # 2. TRADUCCIÓN DE COORDENADAS: Pasamos de Gauss-Kruger (metros) a WGS84 (grados) para Folium
    print("Reproyectando sistema de coordenadas (Meters -> Lat/Lon)...")
    gdf_ruido = gdf_ruido.to_crs(epsg=4326)
    
    # Normalizamos las columnas a minúsculas para trabajar limpio
    gdf_ruido.columns = gdf_ruido.columns.str.lower()

except Exception as e:
    print(f"Error crítico al procesar el archivo geográfico: {e}")
    sys.exit(1)

# 3. Filtrar por el período diurno (buscando en la columna ya normalizada)
gdf_diurno = gdf_ruido[gdf_ruido['periodo'].str.lower().str.contains('diurno', na=False)].copy()

if gdf_diurno.empty:
    print("Error: El filtro 'diurno' dejó el mapa vacío. Valores en columna periodo:", gdf_ruido['periodo'].unique())
    sys.exit(1)

print(f"¡Datos filtrados con éxito! Polígonos listos para dibujar: {len(gdf_diurno)}")

# 4. Función de mapeo cromático con tu escala exacta (usando 'db_lo' del XML)
def obtener_color_personalizado(properties):
    # El XML nos dice que DB_LO ya es un número (Double), no hace falta castear
    dba = properties.get('db_lo', 0)
    
    if dba >= 80:
        return "#1100aa"  # Azul profundo
    elif dba >= 75:
        return "#451c92"
    elif dba >= 70:
        return "#8121ad" 
    elif dba >= 65:
        return "#942a1e"
    elif dba >= 60:
        return "#e74c3c" 
    elif dba >= 55:
        return "#e7723c" 
    elif dba >= 50:
        return "#e7a33c" 
    elif dba >= 45:
        return "#eff312" 
    elif dba >= 40:
        return "#1e9905" 
    elif dba >= 35:
        return "#0bdf63"  # Verde claro
    else:
        return "#44d480"  

# 5. Inicializar el mapa centrado en CABA
mapa = folium.Map(location=[-34.6037, -58.3816], zoom_start=12, tiles='CartoDB positron')

# 6. Renderizar las Isófonas en el mapa
folium.GeoJson(
    gdf_diurno,
    name="Mapa de Ruido Diurno 2018 CABA",
    style_function=lambda feature: {
        'fillColor': obtener_color_personalizado(feature['properties']), 
        'color': obtener_color_personalizado(feature['properties']), 
        'weight': 0.4,
        'fillOpacity': 0.6
    },
    # Mapeamos las etiquetas flotantes usando los nombres exactos del XML en minúsculas
    tooltip=folium.features.GeoJsonTooltip(
        fields=['leyenda', 'comuna', 'db_lo'],
        aliases=['Intensidad: ', 'Comuna: ', 'Mínimo dBA: '],
        style="background-color: white; color: black; font-family: arial; font-size: 15px; padding: 5px;"
    )
).add_to(mapa)

# 7. Guardar el archivo final
folium.LayerControl().add_to(mapa)

# 8 Agregué un índice al costado

from branca.element import Template, MacroElement

plantilla_leyenda = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; background-color: rgba(255, 255, 255, 0.9);
    border-radius: 8px; padding: 12px; font-size: 13px; font-family: "Arial", sans-serif;
    left: 10px; top: 90px; border: 2px solid #bdc3c7; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>
  
  <div class='legend-title' style='font-weight: bold; margin-bottom: 8px; font-size: 14px; color: #2c3e50;'>
    Nivel de Ruido (dBA)
  </div>
  
  <div class='legend-scale'>
    <ul class='legend-labels' style='list-style: none; padding: 0; margin: 0;'>
      <li><span style='background:#1100aa;'></span>&ge; 80 dBA (Extremo)</li>
      <li><span style='background:#451c92;'></span>75 - 80 dBA</li>
      <li><span style='background:#8121ad;'></span>70 - 75 dBA</li>
      <li><span style='background:#942a1e;'></span>65 - 70 dBA</li>
      <li><span style='background:#e74c3c;'></span>60 - 65 dBA</li>
      <li><span style='background:#e7723c;'></span>55 - 60 dBA</li>
      <li><span style='background:#e7a33c;'></span>50 - 55 dBA</li>
      <li><span style='background:#eff312;'></span>45 - 50 dBA</li>
      <li><span style='background:#1e9905;'></span>40 - 45 dBA</li>
      <li><span style='background:#0bdf63;'></span>35 - 40 dBA</li>
      <li><span style='background:#44d480;'></span>&lt; 35 dBA (Tranquilo)</li>
    </ul>
  </div>
</div>

<style type='text/css'>
  .maplegend .legend-labels li {
    margin-bottom: 4px;
    clear: both;
    line-height: 18px;
  }
  .maplegend .legend-labels span {
    display: block;
    float: left;
    width: 16px;
    height: 16px;
    margin-right: 8px;
    border-radius: 3px;
    border: 1px solid rgba(0,0,0,0.2);
  }
</style>
{% endmacro %}
"""

# Creamos el elemento macro de Folium y lo acoplamos al mapa
macro_leyenda = MacroElement()
macro_leyenda._template = Template(plantilla_leyenda)
mapa.add_child(macro_leyenda)


mapa.save("mapa_ruido_diurno_real.html")
print("¡Felicidades! Abrí 'mapa_ruido_diurno_real.html' en tu navegador.")