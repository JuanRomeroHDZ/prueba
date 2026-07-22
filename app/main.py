import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, init_db
from analyzer import analyze_skill_gap

st.set_page_config(page_title="IT Market Analyzer MX - Tijuana", layout="wide")

init_db()

# Estilo personalizado para las tarjetas KPI
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e2130;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #4e8cff;
        margin-bottom: 15px;
    }
    .metric-title { font-size: 14px; color: #a0aabf; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("📍 IT Market Analyzer MX — Tijuana & Baja California")
st.caption("Inteligencia del Mercado Laboral enfocado en tu Ruta Profesional: Infraestructura ➔ Cloud ➔ Ciberseguridad")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM jobs", conn)
conn.close()

tab_analytics, tab_explorer, tab_gap = st.tabs([
    "📊 Mercado TI en Tijuana", 
    "📋 Buscador de Vacantes", 
    "🎯 Mi Perfil vs Mercado"
])

# -------------------------------------------------------------------
# PESTAÑA 1: ANALÍTICA DEL MERCADO LOCAL EN TIJUANA
# -------------------------------------------------------------------
with tab_analytics:
    if df.empty:
        st.info("No hay datos cargados en la base de datos. Ejecuta `test_scraper.py` para recabar información.")
    else:
        # Fila de Indicadores clave (KPIs)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Vacantes Tijuana & Remoto</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            
        with kpi2:
            altas = df[df["prioridad_empresa"] == "🟢 Alta"] if "prioridad_empresa" in df.columns else []
            st.markdown(f'<div class="metric-card"><div class="metric-title">Empresas Prioritarias</div><div class="metric-value">{len(altas)}</div></div>', unsafe_allow_html=True)
            
        with kpi3:
            salarios_validos = df["salario_promedio"].dropna()
            avg_sal = salarios_validos.mean() if not salarios_validos.empty else 0
            st.markdown(f'<div class="metric-card"><div class="metric-title">Salario Promedio</div><div class="metric-value">${avg_sal:,.2f} MXN</div></div>', unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Fuentes Monitoreadas</div><div class="metric-value">{df["fuente"].nunique()}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Gráficos Analíticos
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("🎯 Distribución por Ruta de Carrera")
            if "career_path" in df.columns:
                fig_path = px.pie(df, names="career_path", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_path, width="stretch")
            else:
                fig_area = px.pie(df, names="area", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_area, width="stretch")

        with col_g2:
            st.subheader("🏢 Vacantes por Prioridad de Empresa")
            if "prioridad_empresa" in df.columns:
                df_prio = df["prioridad_empresa"].value_counts().reset_index()
                df_prio.columns = ["Prioridad", "Vacantes"]
                fig_prio = px.bar(df_prio, x="Prioridad", y="Vacantes", color="Prioridad")
                st.plotly_chart(fig_prio, width="stretch")

        st.markdown("---")

        col_g3, col_g4 = st.columns(2)
        
        with col_g3:
            st.subheader("🗣️ Requerimiento de Idioma Inglés")
            fig_ing = px.pie(df, names="ingles", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_ing, width="stretch")

        with col_g4:
            st.subheader("⏳ Experiencia Requerida")
            fig_exp = px.histogram(df, x="experiencia", color="experiencia")
            st.plotly_chart(fig_exp, width="stretch")

# -------------------------------------------------------------------
# PESTAÑA 2: EXPLORADOR Y FILTRADO INTUITIVO
# -------------------------------------------------------------------
with tab_explorer:
    st.subheader("📋 Buscador Inteligente de Vacantes en Tijuana")
    
    if not df.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            rutas_opt = ["Todas"] + list(df["career_path"].dropna().unique()) if "career_path" in df.columns else ["Todas"]
            sel_ruta = st.selectbox("Ruta de Carrera:", rutas_opt)
            
        with col_f2:
            ingles_opts = ["Todos"] + list(df["ingles"].dropna().unique())
            sel_ing = st.selectbox("Nivel de Inglés:", ingles_opts)
            
        with col_f3:
            solo_con_salario = st.checkbox("Mostrar únicamente vacantes con salario publicado", value=False)

        busqueda = st.text_input("🔍 Buscar por Empresa, Puesto o Palabra Clave:", "")

        df_filtered = df.copy()
        
        if sel_ruta != "Todas" and "career_path" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["career_path"] == sel_ruta]
        if sel_ing != "Todos":
            df_filtered = df_filtered[df_filtered["ingles"] == sel_ing]
        if solo_con_salario:
            df_filtered = df_filtered[df_filtered["salario_promedio"].notnull() & (df_filtered["salario_promedio"] > 0)]
        if busqueda:
            term = busqueda.lower()
            df_filtered = df_filtered[
                df_filtered["puesto"].str.lower().str.contains(term, na=False) |
                df_filtered["empresa"].str.lower().str.contains(term, na=False) |
                df_filtered["area"].str.lower().str.contains(term, na=False)
            ]

        # Columnas a desplegar en la tabla
        cols_w = ["prioridad_empresa", "empresa", "puesto", "career_path", "salario_promedio", "experiencia", "ingles", "fuente", "url"]
        available_cols = [c for c in cols_w if c in df_filtered.columns]
        
        df_show = df_filtered[available_cols].copy()

        if "salario_promedio" in df_show.columns:
            df_show["salario_promedio"] = df_show["salario_promedio"].apply(
                lambda x: f"${x:,.2f} MXN" if pd.notnull(x) and x > 0 else "No publicado"
            )

        st.dataframe(
            df_show, 
            column_config={
                "url": st.column_config.LinkColumn("Enlace Oferta")
            },
            hide_index=True,
            use_container_width=True
        )

# -------------------------------------------------------------------
# PESTAÑA 3: COMPARATIVA DE PERFIL (SKILL GAP)
# -------------------------------------------------------------------
with tab_gap:
    st.subheader("🎯 Tu Perfil vs El Mercado de Tijuana")
    gap = analyze_skill_gap()
    
    col_gap1, col_gap2 = st.columns([1, 2])
    
    with col_gap1:
        st.metric("Alineación con el Mercado", f"{gap['match_percentage']}%")
        st.markdown("### ❌ Tecnologías Sugeridas a Aprender")
        for skill in gap["missing_skills"]:
            st.markdown(f"- `{skill}`")

    with col_gap2:
        if gap["top_market_skills"]:
            st.markdown("### 📈 Habilidades Más Demandadas")
            df_skills = pd.DataFrame(list(gap["top_market_skills"].items()), columns=["Tecnología", "Demandante"])
            fig_skills = px.bar(df_skills, x="Tecnología", y="Demandante", color="Demandante")
            st.plotly_chart(fig_skills, width="stretch")
