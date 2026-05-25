# 🎧 Mapa Interactivo de Contaminación Acústica - CABA

Un dashboard geoespacial interactivo que visualiza el impacto acústico de fuentes móviles en la Ciudad Autónoma de Buenos Aires, permitiendo comparar los niveles de ruido entre el período diurno y nocturno.

🌐 **[Ver el Dashboard en Vivo (Live Demo)](https://tonago234.github.io/mapa-acustico-caba/index.html)** 

## 🚀 Arquitectura y Características Principales

Este proyecto no es solo una visualización estática, sino un pipeline de ingeniería de datos GIS optimizado para correr en el navegador sin saturar el DOM:

* **Manejo de Capas Mutuamente Excluyentes:** Implementación de `GroupedLayerControl` para alternar fluidamente entre los turnos diurnos y nocturnos mediante *Radio Buttons*, garantizando una interfaz limpia.
* **Optimización Geométrica:** Aplicación del algoritmo de Douglas-Peucker (`.simplify()`) sobre los polígonos base para reducir en un porcentaje masivo la cantidad de vértices redundantes, bajando drásticamente el peso del archivo HTML final y mejorando los FPS del navegador.
* **Reproyección de Coordenadas (CRS):** Transformación nativa de las coordenadas proyectadas Gauss-Kruger (EPSG:22195) a grados decimales WGS84 (EPSG:4326) requeridos por los estándares web.
* **Camera Lock & Padding Espacial:** Restricción de la cámara de Leaflet.js (`max_bounds`) calculada dinámicamente con un *padding* cartográfico, lo que evita que el usuario se pierda en el mapa base global mientras permite explorar libremente los límites de la ciudad.
* **Máscara de Contención (Bitmasking Visual):** Generación de un polígono global invertido (`.difference()`) para enmascarar el Gran Buenos Aires y el Río de la Plata, forzando la atención visual sobre la huella de CABA.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Procesamiento Espacial:** `GeoPandas`, `Pandas`, `Shapely`
* **Renderizado Web / UI:** `Folium`, `Leaflet.js`, `branca`

## 📂 Fuentes de Datos

Los datos vectoriales (formato Shapefile) fueron obtenidos a través de [BA Data](https://data.buenosaires.gob.ar/dataset/mapa-ruido), el portal oficial de datos abiertos del Gobierno de la Ciudad de Buenos Aires. Representan el nivel sonoro continuo equivalente a largo plazo, validado por la Agencia de Protección Ambiental (APrA).

## ⚙️ Instalación y Uso Local

Si deseás clonar este repositorio y correr el pipeline de procesamiento en tu propia máquina:

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:tonago234/mapa-acustico-caba.git
   cd mapa-acustico-caba

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # En Windows (Git Bash)

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt

4. **Ejecutar el pipeline:**
   ```bash
   python mapa.py

El script procesará los shapefiles y generará el archivo dashboard_ruido_caba.html en la misma carpeta.

Autor: Tomás Nahuel Villegas González - [Linkedin](https://www.linkedin.com/in/tomas-n-villegas-g/)