# EDA — Subastas Públicas de Inmuebles en España

![alt text](image-1.png)


> **¿Una oportunidad real de compra?**  
> Análisis exploratorio de datos sobre subastas públicas de inmuebles publicadas en el Portal del BOE (oct–dic 2025)

---

## Descripción

Este proyecto analiza las subastas públicas de inmuebles publicadas en el **Portal de Subastas del Boletín Oficial del Estado** ([subastas.boe.es](https://subastas.boe.es)) durante el trimestre octubre–diciembre 2025.

---

## Hipótesis

> *"Las subastas de inmuebles de organismos tributarios (AEAT y Recaudación Tributaria) en España entre octubre y diciembre 2025 se ofertan mayoritariamente por debajo del 50% de su valor de tasación"*

### Resultado: Hipótesis confirmada

**El 89.4% de los inmuebles analizados salen a subasta por debajo del 50% de su tasación**, con un descuento medio del **30.6%**.

---

## 📊 Datos

| Campo | Valor |
|-------|-------|
| Fuente | Portal de Subastas del BOE |
| URL | [subastas.boe.es](https://subastas.boe.es) |
| Período | Octubre — Diciembre 2025 |
| Registros totales scrapeados | 4.726 |
| Registros analizados | 498 |
| Organismos | AEAT + Recaudación Tributaria |
| Método de obtención | Web scraping con Python |

---

## 🔍 Principales hallazgos

-  **89.4%** de subastas tributarias salen por debajo del 50% de tasación
-  El descuento estándar es del **20%** — el mínimo legal aplicado por la AEAT
- El depósito previo siempre es el **5%** del valor de subasta (correlación 1.00)
- El descuento es **independiente del valor del inmueble** (correlación -0.08)
- La AEAT concentra el **84.1%** de las subastas tributarias analizadas
- La duración estándar es **20 días** — plazo legal establecido para subastas electrónicas
- ⚠️ Un descuento alto puede indicar **cargas ocultas** que el comprador debe investigar

---

## 🛠️ Tecnologías utilizadas

| Herramienta | Uso |
|-------------|-----|
| Python 3.11 | Lenguaje principal |
| cloudscraper | Web scraping con bypass Cloudflare |
| BeautifulSoup | Parsing HTML |
| pandas | Manipulación de datos |
| numpy | Cálculos numéricos |
| matplotlib | Visualizaciones |
| seaborn | Visualizaciones estadísticas |
| scipy | Análisis estadístico |
| uv | Gestión del entorno virtual |
| Jupyter Notebook | Desarrollo interactivo |

---

## 📁 Estructura del proyecto

```
proyecto_eda_subastas/
├── src/
│   ├── data/
│   │   ├── subastas_inmuebles_oct2025.csv
│   │   ├── subastas_inmuebles_nov2025.csv
│   │   ├── subastas_inmuebles_dic2025.csv
│   │   └── subastas_analisis_final.csv
│   ├── img/
│   │   └── slide1.png        ← imagen1 para slide1 de PresentacionEDA.pptx
│   │   └── slide2.png        ← imagen2 para slide2 de PresentacionEDA.pptx
│   │   └── slide3.png        ← imagen3 para slide3 de PresentacionEDA.pptx
│   │   └── slide4.png        ← imagen4 para slide4 de PresentacionEDA.pptx
│   │   └── slide5.png        ← imagen5 para slide5 de PresentacionEDA.pptx
│   │   └── slide6.png        ← imagen6 para slide6 de PresentacionEDA.pptx
│   ├── notebooks/
│   │   └── Web_Scraping.ipynb       ← scraping paso a paso
│   ├── utils/
│   │   ├── bootcampviztools.py      ← funciones de visualización del bootcamp
│   │   └── funciones.py             ← funciones propias de limpieza y visualización
│   │   └── inspeccion.html          ← inspeccion del portal web BOE para Web Scraping
│   └── memoria.ipynb                ← notebook principal del EDA
├── PresentacionEDA.pptx             ← presentación de resultados
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 🚀 Cómo ejecutar el proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/nadia0207/Proyecto_EDA_Subastas_BOE.git
cd proyecto_eda_subastas
```

### 2. Instalar dependencias con uv
```bash
uv sync
```

### 3. Ejecutar el scraping (opcional — el CSV ya está incluido)
```bash
uv run jupyter notebook src/notebooks/Web_Scraping.ipynb
```

### 4. Ver el análisis completo
```bash
uv run jupyter notebook src/memoria.ipynb
```

---

## 📈 Visualizaciones destacadas

El análisis incluye:
- Distribución del descuento sobre tasación (histograma + KDE + boxplot)
- Scatter plot valor subasta vs tasación en escala logarítmica
- Evolución temporal de subastas y descuentos (oct–dic 2025)
- Heatmap de correlación entre variables numéricas
- Pairplot de relaciones entre variables
- Contraste de hipótesis con gráficos de proporción

---

## ⚠️ Limitaciones

- Solo se analizaron organismos tributarios (AEAT y Recaudación) por ser los únicos con datos económicos completos en el portal
- Período limitado a 3 meses (oct–dic 2025)
- No se dispone de datos sobre el precio final de adjudicación
- Las subastas con varios lotes no pudieron analizarse individualmente

---

## 👩‍💻 Autora

**Nadia Llamoca**  
Bootcamp Data Science — TheBridge  
2025

---

## 📄 Licencia

Este proyecto es de uso educativo. Los datos provienen del Portal de Subastas del BOE, fuente pública oficial del Estado español, sujeta a la [Ley de Reutilización de la Información del Sector Público](https://www.boe.es/eli/es/l/2007/11/16/37/con).
