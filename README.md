# 📍 IT Market Analyzer MX — Tijuana & Baja California

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Debian](https://img.shields.io/badge/OS-Debian_Linux-red.svg)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg)

**IT Market Analyzer MX** es un sistema de Inteligencia de Mercado diseñado para recopilar, normalizar y analizar vacantes laborales del sector de Tecnologías de la Información en México, con enfoque especializado en **Tijuana, Baja California** y posiciones **100% Remotas**.

El proyecto rastrea la demanda real del mercado para trazar la ruta de crecimiento profesional:  
**Infraestructura de Redes → Cloud & Automatización → Ciberseguridad & SOC**

---

## 🌟 Características Principales

* **Filtro de Precisión Técnica:** Bloquea ofertas no relacionadas (ventas, marketing, hotelería, soporte no TI).
* **Deduplicación Inteligente (SHA-256):** Algoritmo de *Fingerprinting* para evitar vacantes duplicadas entre múltiples bolsas de trabajo.
* **Geolocalización Estricta:** Filtrado específico para Tijuana, Mexicali y plazas remotas internacionales.
* **Matriz de Prioridad de Empresas:** Clasifica empleadores locales en categorías Alta, Media y Normal (Maquiladoras, Integradores MSP y Data Centers).
* **Análisis de Brecha de Habilidades (Skill Gap):** Comparativa automatizada entre un perfil profesional definido (`my_profile.json`) y las tecnologías más solicitadas.
* **Dashboard Interactivo:** Interfaz construida en Streamlit con métricas KPI, gráficos en Plotly y tabla interactiva.

---

## 🛠️ Arquitectura del Sistema

```text
IT-Market-Analyzer-MX/
├── app/
│   ├── main.py             # Dashboard en Streamlit
│   ├── database.py         # Inicialización y esquema de SQLite
│   ├── analyzer.py         # Motor de análisis de brecha de habilidades
│   ├── scraper/
│   │   └── tijuana.py      # Conectores multi-fuente (Playwright + BS4)
│   └── utils/
│       └── parser.py       # Normalizador, extractor regex y Fingerprint SHA-256
├── database/
│   └── jobs.db             # Base de datos SQLite
├── scripts/
│   └── setup_cron.sh       # Script de automatización para Debian Linux
├── my_profile.json         # Perfil del desarrollador
├── test_scraper.py         # Pipeline principal de extracción
├── requirements.txt
└── README.md

```

---

## 🚀 Instalación y Uso en Linux (Debian)

### 1. Clonar el repositorio y preparar el entorno

```bash
git clone [https://github.com/TU_USUARIO/IT-Market-Analyzer-MX.git](https://github.com/TU_USUARIO/IT-Market-Analyzer-MX.git)
cd IT-Market-Analyzer-MX

python3 -m venv it-market-env
source it-market-env/bin/activate
pip install -r requirements.txt
playwright install chromium

```

### 2. Ejecutar la recolección de datos

```bash
PYTHONPATH=. python3 test_scraper.py

```

### 3. Iniciar el Dashboard

```bash
PYTHONPATH=. streamlit run app/main.py

```

---

## 📈 Fuentes Monitoreadas

* **Bolsas de Trabajo Local / Nacional:** Empleo Nuevo, OCC Mundial, Computrabajo, Talenteca, Jooble, Indeed, Glassdoor, LinkedIn Jobs.
* **Portales Remotos Internacionales:** Remote.co.
* **Empresas Clave Objetivo:** Enteracloud, Nerium, Schneider Electric, Thermo Fisher, KIO Networks, SONDA, Medtronic, Jabil, Honeywell, Skyworks.
EOF

```

---
