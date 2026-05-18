import geopandas as gpd
import pandas as pd
import folium
import sys
from branca.element import Template, MacroElement

print("Iniciando el pipeline de procesamiento acústico multicapa...")

def procesar_shapefile(ruta_archivo):
    """Función auxiliar para reutilizar la lógica de limpieza en ambos archivos"""
    try:
        gdf = gpd.read_file(ruta_archivo)
        gdf = gdf.to_crs(epsg=4326) # Reproyección obligatoria a grados
        gdf.columns = gdf.columns.str.lower() # Normalizamos columnas
        gdf['db_lo_num'] = pd.to_numeric(gdf['db_lo'], errors='coerce').fillna(0)
        return gdf
    except Exception as e:
        print(f"Error crítico al procesar {ruta_archivo}: {e}")
        sys.exit(1)

# 1. Cargar y procesar ambos datasets nativos
gdf_diurno = procesar_shapefile("mapa_de_ruido_diurno.shp")
gdf_nocturno = procesar_shapefile("mapa_de_ruido_nocturno.shp")

# 2. Función de mapeo cromático personalizado
def obtener_color_personalizado(properties):
    dba = properties.get('db_lo_num', 0)
    if dba >= 80: return "#1100aa"
    elif dba >= 75: return "#451c92"
    elif dba >= 70: return "#8121ad" 
    elif dba >= 65: return "#942a1e"
    elif dba >= 60: return "#e74c3c" 
    elif dba >= 55: return "#e7723c" 
    elif dba >= 50: return "#e7a33c" 
    elif dba >= 45: return "#eff312" 
    elif dba >= 40: return "#1e9905" 
    elif dba >= 35: return "#0bdf63"  
    else: return "#44d480"  

# 3. Inicializar el mapa base centrado en CABA
mapa = folium.Map(location=[-34.6037, -58.3816], zoom_start=12, tiles='CartoDB positron')

# === EL FIX: Creamos dos instancias de tooltip totalmente independientes ===
campos_tt = ['db_rango', 'comuna', 'db_lo_num']
aliases_tt = ['Rango dBA: ', 'Comuna: ', 'Mínimo dBA: ']
estilo_tt = "background-color: white; color: black; font-family: arial; font-size: 13px; padding: 5px;"

tooltip_diurno = folium.features.GeoJsonTooltip(fields=campos_tt, aliases=aliases_tt, style=estilo_tt)
tooltip_nocturno = folium.features.GeoJsonTooltip(fields=campos_tt, aliases=aliases_tt, style=estilo_tt)

# 4. Creación de contenedores de capas (Feature Groups)
capa_diurna = folium.FeatureGroup(name="☀️ Turno Diurno (07:00 a 22:00)", show=True)
capa_nocturna = folium.FeatureGroup(name="🌙 Turno Nocturno (22:00 a 07:00)", show=False)

# Inyectamos los polígonos diurnos con su respectivo tooltip único
folium.GeoJson(
    gdf_diurno,
    style_function=lambda feature: {
        'fillColor': obtener_color_personalizado(feature['properties']), 
        'color': obtener_color_personalizado(feature['properties']), 
        'weight': 0.4, 'fillOpacity': 0.6
    },
    tooltip=tooltip_diurno
).add_to(capa_diurna)

# Inyectamos los polígonos nocturnos con su respectivo tooltip único
folium.GeoJson(
    gdf_nocturno,
    style_function=lambda feature: {
        'fillColor': obtener_color_personalizado(feature['properties']), 
        'color': obtener_color_personalizado(feature['properties']), 
        'weight': 0.4, 'fillOpacity': 0.6
    },
    tooltip=tooltip_nocturno
).add_to(capa_nocturna)

# Acoplamos las capas al mapa
capa_diurna.add_to(mapa)
capa_nocturna.add_to(mapa)

# 5. El Botón Conmutador (Layer Control) - Ahora sí va a renderizar correctamente
folium.LayerControl(position='topright', collapsed=False).add_to(mapa)

# 6. Inyección de Leyenda HTML
plantilla_leyenda = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; background-color: rgba(255, 255, 255, 0.9);
    border-radius: 8px; padding: 12px; font-size: 13px; font-family: "Arial", sans-serif;
    left: 10px; top: 90px; border: 2px solid #bdc3c7; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>
  <div class='legend-title' style='font-weight: bold; margin-bottom: 8px; font-size: 14px; color: #2c3e50;'>Nivel de Ruido (dBA)</div>
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
  .maplegend .legend-labels li { margin-bottom: 4px; clear: both; line-height: 18px; }
  .maplegend .legend-labels span { display: block; float: left; width: 16px; height: 16px; margin-right: 8px; border-radius: 3px; border: 1px solid rgba(0,0,0,0.2); }
</style>
{% endmacro %}
"""
macro_leyenda = MacroElement()
macro_leyenda._template = Template(plantilla_leyenda)
mapa.add_child(macro_leyenda)

# 7. Guardar el archivo final
mapa.save("dashboard_ruido_caba.html")
print("¡Dashboard corregido con éxito! Volvé a abrir 'dashboard_ruido_caba.html'.")