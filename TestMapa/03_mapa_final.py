import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from sklearn.ensemble import RandomForestRegressor
from shapely.geometry import Polygon

print("Iniciando el motor del mapa predictivo...")

# 1. CARGA Y PREPARACIÓN EXPRESO DE DATOS
df = pd.read_csv("dataset_inmobiliario_acustico_limpio.csv")

# Replicamos el procesamiento numérico de los barrios
df_ml = pd.get_dummies(df, columns=['barrio_1'], drop_first=True)

X = df_ml.drop(['preciousd', 'precio_x_m2'], axis=1)
y = df_ml['precio_x_m2']

# 2. RE-ENTRENAMIENTO RÁPIDO DEL MODELO
print("Entrenando la Inteligencia Artificial...")
modelo = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
modelo.fit(X, y)

# 3. CÁLCULO DE RESIDUOS (Predicción vs Realidad)
print("Calculando desvíos del mercado inmobiliario...")
df['precio_predicho'] = modelo.predict(X)
df['desvio'] = df['precio_x_m2'] - df['precio_predicho']

# 4. ARMADO DEL MAPA INTERACTIVO CON MÁSCARA
print("Dibujando el mapa interactivo de CABA...")

limites_caba = [
    [-34.760, -58.590],
    [-34.470, -58.280]  
]

mapa_final = folium.Map(
    location=[-34.6037, -58.3816], zoom_start=12, min_zoom=11,
    tiles='CartoDB positron', max_bounds=True,
    min_lat=limites_caba[0][0], max_lat=limites_caba[1][0],
    min_lon=limites_caba[0][1], max_lon=limites_caba[1][1]
)

print("Optimizando máscara regional...")
try:
    barrios_caba = gpd.read_file("barrios.geojson")
    # Simplificamos la silueta exterior para acelerar el renderizado del fondo
    silueta_caba = barrios_caba.dissolve().simplify(tolerance=0.0001, preserve_topology=True)
    mundo = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90)])
    mascara_geom = mundo.difference(silueta_caba.iloc[0])
    gdf_mascara = gpd.GeoDataFrame(geometry=[mascara_geom], crs="EPSG:4326")
    
    folium.GeoJson(
        gdf_mascara, name="Máscara Exterior",
        style_function=lambda x: {'fillColor': '#e5e8e8', 'color': '#bdc3c7', 'weight': 1.5, 'fillOpacity': 0.7},
        control=False
    ).add_to(mapa_final)
except Exception as e:
    print(f"Aviso: No se pudo generar la máscara, continuando sin ella. Motivo: {e}")

# Creamos el clúster y lo atamos a mapa_final
cluster = MarkerCluster(name="Propiedades Analizadas").add_to(mapa_final)

# Muestra aleatoria para no saturar el renderizado en el navegador
df_muestra = df.sample(n=2000, random_state=42)

for idx, fila in df_muestra.iterrows():
    if fila['desvio'] < -150:
        color_marcador = 'green'
        condicion = "Oportunidad (Subvaluado)"
    elif fila['desvio'] > 150:
        color_marcador = 'red'
        condicion = "Sobrevaluado"
    else:
        color_marcador = 'gray'
        condicion = "Precio de Mercado Ajustado"
        
    popup_texto = f"""
    <div style='font-family: Arial, sans-serif; width: 200px;'>
        <h4><b>{condicion}</b></h4>
        <hr style='margin: 5px 0;'>
        <b>Barrio:</b> {fila['barrio_1']}<br>
        <b>Ambientes:</b> {int(fila['ambientes'])} ({int(fila['m2total'])} m²)<br>
        <b>Ruido Base:</b> {int(fila['db_lo_num'])} dBA<br>
        <hr style='margin: 5px 0;'>
        <b>Precio Real m²:</b> USD {int(fila['precio_x_m2'])}<br>
        <b>Predicho por IA:</b> USD {int(fila['precio_predicho'])}<br>
        <b>Diferencia:</b> USD {int(fila['desvio'])}
    </div>
    """
    
    folium.CircleMarker(
        location=[fila['latitud'], fila['longitud']],
        radius=5,
        color=color_marcador,
        fill=True,
        fill_color=color_marcador,
        fill_opacity=0.7,
        popup=folium.Popup(popup_texto, max_width=250)
    ).add_to(cluster)

# 5. EXPORTACIÓN
mapa_final.save("mapa_oportunidades.html")
print("✨ ¡Éxito total! Archivo 'mapa_oportunidades.html' generado con máscara y restricciones.")