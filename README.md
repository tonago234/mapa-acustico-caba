# 🏙️🎧 Pipeline de Ciencia de Datos Espaciales: Impacto Acústico y Predicción Inmobiliaria en CABA

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=for-the-badge&logo=geopandas&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=folium&logoColor=white)

Un ecosistema analítico y predictivo integrado que procesa el impacto de la contaminación acústica en la Ciudad Autónoma de Buenos Aires y evalúa, mediante Machine Learning, cómo el entorno urbano y el nivel de ruido diurno modelan el precio del metro cuadrado en el mercado inmobiliario.

---

## 🌐 Ver los Dashboards en Vivo (Live Demos)
* **[Link al Mapa Predictivo de Oportunidades Inmobiliarias](TU_LINK_ACA)**
* **[Link al Dashboard de Contaminación Acústica (Diurno/Nocturno)](TU_LINK_ACA)**

---

## 🚀 Arquitectura del Proyecto y Características Principales

Este repositorio está estructurado como un pipeline modular de ingeniería y ciencia de datos, dividido en tres fases clave:

### Fase 1: Ingeniería de Datos GIS y Optimización (`mapa.py` & `01_cruce_espacial.ipynb`)
Diseñado para procesar datos geométricos pesados a gran escala y optimizarlos para su fluidez en el navegador:
* **Optimización Geométrica:** Aplicación del algoritmo de Douglas-Peucker (`.simplify()`) sobre los polígonos base de ruido para reducir masivamente la cantidad de vértices redundantes, bajando drásticamente el peso del archivo final.
* **Manejo de Capas Mutuamente Excluyentes:** Implementación de `GroupedLayerControl` para alternar fluidamente entre los mapas de ruido diurnos y nocturnos mediante botones de radio.
* **Reproyección de Coordenadas (CRS):** Transformación nativa de coordenadas proyectadas Gauss-Kruger (EPSG:22195) a grados decimales WGS84 (EPSG:4326) requeridos por los estándares web cartográficos.
* **Camera Lock & Máscara de Contención:** Restricción de la cámara de Leaflet.js (`max_bounds`) combinada con una máscara regional invertida (`.difference()`) para tapar el Gran Buenos Aires y el Río de la Plata, forzando el foco visual exclusivamente en CABA.

### Fase 2: Modelado Predictivo de Machine Learning (`02_modelo_predictivo.ipynb`)
* **El Cruce Espacial (Spatial Join):** Mediante GeoPandas se intersectaron geométricamente miles de puntos de departamentos en venta con los polígonos de decibeles de ruido correspondientes a su ubicación exacta.
* **Algoritmo:** Entrenamiento de un modelo `RandomForestRegressor` (Bosque Aleatorio) de Scikit-Learn para predecir la variable objetivo: **Precio por Metro Cuadrado (`precio_x_m2`)**.
* **Métricas del Modelo:**
  * **R² Score (Precisión):** 71.24% de la variación de los precios explicada por el modelo.
  * **MAE (Error Absoluto Medio):** ~351 USD/m², un margen altamente competitivo considerando que el dataset no cuenta con variables cualitativas (estado del depto, amenities, etc.).

### Fase 3: Análisis de Residuos y Mapa de Oportunidades (`03_mapa_final.py`)
El modelo se utiliza para auditar el mercado inmobiliario calculando los desvíos (Precio Real - Precio Predicho):
* 🟢 **Verde - Oportunidad (Subvaluado):** El precio real es significativamente menor de lo que la IA predice según su entorno y tamaño.
* 🔴 **Rojo - Sobrevaluado:** Propiedades con precios inflados respecto a la predicción del modelo.
* ⚪ **Gris - Precio de Mercado:** Valores alineados con la tendencia del entorno.

---

## 📊 Key Insights (Conclusiones Analíticas)

Al analizar la importancia de las variables (*Feature Importance*) en el algoritmo predictivo, surgieron hallazgos clave sobre el comportamiento del mercado porteño:

1. **La Ubicación Estructural manda (57.7%):** La latitud y la longitud combinadas representan más de la mitad del peso en la formación del precio.
2. **El "Efecto Puerto Madero" (16.9%):** El modelo debió aislar este barrio de forma categórica (One-Hot Encoding) debido a que maneja una dinámica de precios despegada del resto de la ciudad.
3. **El impacto real del Ruido (3.5%):** Contrario a la hipótesis inicial, la contaminación acústica (`db_lo_num`) tiene un peso marginal. **Insight de negocio:** El mercado inmobiliario en CABA prioriza fuertemente el estatus, la demanda y la conectividad por encima del confort acústico. Los compradores validan precios altos por vivir en el epicentro de polos comerciales o avenidas (ej. Palermo) a pesar de los niveles elevados de decibeles.

<img width="989" height="590" alt="variablesPorPrecio" src="https://github.com/user-attachments/assets/bc69e463-50f5-43c1-a964-d2353ba73e0e" />

---

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.x
* **Procesamiento Espacial:** GeoPandas, Pandas, Shapely
* **Machine Learning:** Scikit-Learn
* **Visualización y UI:** Folium (Leaflet.js), Matplotlib, Seaborn, branca

---

## 📂 Fuentes de Datos
Los datos vectoriales en formato Shapefile fueron obtenidos a través de **BA Data**, el portal oficial de datos abiertos del Gobierno de la Ciudad de Buenos Aires:
* Mapa de Ruido Diurno y Nocturno - Validado por la Agencia de Protección Ambiental (APrA).
* Registro de departamentos en venta (Histórico 2018).

---

## ⚙️ Instalación y Uso Local

Para clonar este repositorio y ejecutar el pipeline completo en tu máquina:

```bash
# 1. Clonar el repositorio
git clone [https://github.com/tonago234/Test-mapa-polucion-CABA.git](https://github.com/tonago234/Test-mapa-polucion-CABA.git)
cd Test-mapa-polucion-CABA

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/Scripts/activate  # En Windows (Git Bash)

# 3. Instalar dependencias
pip install -r requirements.txt

