import geopandas as gpd
import folium

barrios_caba = gpd.read_file("barrios.geojson")

# 2. Crear mapa base centrado en el Obelisco
mapa = folium.Map(location=[-34.6037, -58.3816], zoom_start=12, tiles='CartoDB positron')

folium.GeoJson(
    barrios_caba,
    name="Barrios CABA",
    style_function=lambda feature: {
        'fillColor': '#3186cc',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3
    }
).add_to(mapa)

folium.LayerControl().add_to(mapa)
mapa.save("mapa_barrios_caba.html")

print("¡Listo! Abrí el archivo mapa_barrios_caba.html en tu navegador.")