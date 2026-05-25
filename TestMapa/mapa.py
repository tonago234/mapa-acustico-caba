import geopandas as gpd
import pandas as pd
import folium
import sys
from branca.element import Template, MacroElement
from folium.plugins import GroupedLayerControl

print("Iniciando pipeline GIS...")

def procesar_shapefile_optimizado(ruta_archivo):
    """Carga, proyecta, filtra columnas y simplifica geometrías para optimizar el HTML"""
    try:
        # 1. Carga nativa
        gdf = gpd.read_file(ruta_archivo)
        
        # 2. Poda de columnas inmediata para liberar memoria RAM
        gdf.columns = gdf.columns.str.lower()
        columnas_criticas = ['geometry', 'db_lo', 'db_rango', 'leyenda', 'comuna', 'periodo']
        columnas_a_mantener = [c for c in columnas_criticas if c in gdf.columns]
        gdf = gdf[columnas_a_mantener].copy()
        
        # 3. Reproyección indispensable para Folium
        gdf = gdf.to_crs(epsg=4326)
        
        # 4. SIMPLIFICACIÓN GEOMÉTRICA: Reduce vértices drásticamente sin pérdida visual perceptible
        # tolerance=0.00005 equivale a ~5 metros de precisión, ideal para zoom urbano (11-14)
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.00005, preserve_topology=True)
        
        # 5. Normalización del tipo de dato
        if 'db_lo' in gdf.columns:
            gdf['db_lo_num'] = pd.to_numeric(gdf['db_lo'], errors='coerce').fillna(0)
        else:
            gdf['db_lo_num'] = 0
            
        return gdf
    except Exception as e:
        print(f"Error crítico al optimizar {ruta_archivo}: {e}")
        sys.exit(1)

# Cargar y optimizar los pesados sets de datos vectoriales
gdf_diurno = procesar_shapefile_optimizado("mapa_de_ruido_diurno.shp")
gdf_nocturno = procesar_shapefile_optimizado("mapa_de_ruido_nocturno.shp")

# Función de mapeo cromático personalizado
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

# Inicializar mapa base con restricciones de cámara
limites_caba = [
    [-34.760, -58.590],
    [-34.470, -58.280]  
]

mapa = folium.Map(
    location=[-34.6037, -58.3816], zoom_start=12, min_zoom=11,
    tiles='CartoDB positron', max_bounds=True,
    min_lat=limites_caba[0][0], max_lat=limites_caba[1][0],
    min_lon=limites_caba[0][1], max_lon=limites_caba[1][1]
)

# Construir Máscara de Contención simplificada para el Gran Buenos Aires
print("Optimizando máscara regional...")
try:
    barrios_caba = gpd.read_file("barrios.geojson")
    # Simplificamos la silueta exterior para acelerar el renderizado del fondo
    silueta_caba = barrios_caba.dissolve().simplify(tolerance=0.0001, preserve_topology=True)
    from shapely.geometry import Polygon
    mundo = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90)])
    mascara_geom = mundo.difference(silueta_caba.iloc[0])
    gdf_mascara = gpd.GeoDataFrame(geometry=[mascara_geom], crs="EPSG:4326")
    
    folium.GeoJson(
        gdf_mascara, name="Máscara Exterior",
        style_function=lambda x: {'fillColor': '#e5e8e8', 'color': '#bdc3c7', 'weight': 1.5, 'fillOpacity': 0.7},
        control=False
    ).add_to(mapa)
except Exception as e:
    print(f"Aviso: No se pudo generar la máscara, continuando sin ella. Motivo: {e}")

# Instanciación de Tooltips independientes de bajo peso
campos_tt = ['db_rango', 'leyenda', 'comuna', 'db_lo_num']
aliases_tt = ['Rango dBA: ', 'Intensidad: ', 'Comuna: ', 'Mínimo dBA: ']
estilo_tt = "background-color: white; color: black; font-family: arial; font-size: 13px; padding: 5px;"

tooltip_diurno = folium.features.GeoJsonTooltip(fields=campos_tt, aliases=aliases_tt, style=estilo_tt)
tooltip_nocturno = folium.features.GeoJsonTooltip(fields=campos_tt, aliases=aliases_tt, style=estilo_tt)

# Empaquetado en Feature Groups mutuamente excluyentes
capa_diurna = folium.FeatureGroup(name="☀️ Turno Diurno (07:00 a 22:00)", show=True)
capa_nocturna = folium.FeatureGroup(name="🌙 Turno Nocturno (22:00 a 07:00)", show=False)

folium.GeoJson(
    gdf_diurno,
    style_function=lambda feature: {'fillColor': obtener_color_personalizado(feature['properties']), 'color': obtener_color_personalizado(feature['properties']), 'weight': 0.3, 'fillOpacity': 0.55},
    tooltip=tooltip_diurno
).add_to(capa_diurna)

folium.GeoJson(
    gdf_nocturno,
    style_function=lambda feature: {'fillColor': obtener_color_personalizado(feature['properties']), 'color': obtener_color_personalizado(feature['properties']), 'weight': 0.3, 'fillOpacity': 0.55},
    tooltip=tooltip_nocturno
).add_to(capa_nocturna)

capa_diurna.add_to(mapa)
capa_nocturna.add_to(mapa)

GroupedLayerControl(groups={'Turnos de Monitoreo': [capa_diurna, capa_nocturna]}, exclusive_groups=True, collapsed=False).add_to(mapa)

# Inyección de Leyenda HTML Estática
plantilla_leyenda = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; background-color: rgba(255, 255, 255, 0.9);
    border-radius: 8px; padding: 12px; font-size: 13px; font-family: "Arial", sans-serif;
    left: 10px; top: 40px; border: 2px solid #bdc3c7; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>
  <div class='legend-title' style='font-weight: bold; margin-bottom: 8px; font-size: 14px; color: #2c3e50;'>Nivel de Ruido (dBA)</div>
  <div class='legend-scale'>
    <ul class='legend-labels' style='list-style: none; padding: 0; margin: 0;'>
      <li><span style='background:#1100aa;'></span>&ge; 80 dBA (Extremo)</li>
      <li><span style='background:#451c92;'></span>75 - 79 dBA</li>
      <li><span style='background:#8121ad;'></span>70 - 74 dBA</li>
      <li><span style='background:#942a1e;'></span>65 - 69 dBA</li>
      <li><span style='background:#e74c3c;'></span>60 - 64 dBA</li>
      <li><span style='background:#e7723c;'></span>55 - 59 dBA</li>
      <li><span style='background:#e7a33c;'></span>50 - 54 dBA</li>
      <li><span style='background:#eff312;'></span>45 - 49 dBA</li>
      <li><span style='background:#1e9905;'></span>40 - 44 dBA</li>
      <li><span style='background:#0bdf63;'></span>35 - 39 dBA</li>
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

mapa.save("index.html")
print("¡Pipeline finalizado! archivo generado: index.html.")