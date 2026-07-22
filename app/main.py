import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, init_db
from analyzer import analyze_skill_gap

st.set_page_config(page_title="IT Market Analyzer MX", layout="wide")

init_db()

st.title("📊 IT Market Analyzer MX")
st.markdown("Análisis del mercado laboral de TI en México: Infraestructura, Redes, Cloud y Ciberseguridad.")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM jobs", conn)
conn.close()

# Sidebar
st.sidebar.header("Filtros")
area_filter = st.sidebar.multiselect("Área de TI", df["area"].unique() if not df.empty else [])

if not df.empty and area_filter:
    df = df[df["area"].isin(area_filter)]

# Metricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Vacantes Analizadas", len(df))
avg_salary = df["salario_promedio"].dropna().mean() if not df.empty and "salario_promedio" in df else 0
col2.metric("Salario Promedio", f"${avg_salary:,.2f} MXN" if avg_salary > 0 else "N/A")
col3.metric("Fuentes Monitoreadas", df["fuente"].nunique() if not df.empty else 0)

st.markdown("---")

# Seccion de analisis
if not df.empty:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Distribución por Área")
        fig_area = px.pie(df, names="area", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_area, use_container_width=True)
        
    with col_right:
        st.subheader("Top Empresas Contratando")
        top_empresas = df["empresa"].value_counts().head(10).reset_index()
        top_empresas.columns = ["Empresa", "Vacantes"]
        fig_emp = px.bar(top_empresas, x="Vacantes", y="Empresa", orientation="h", color="Vacantes")
        st.plotly_chart(fig_emp, use_container_width=True)
else:
    st.info("No hay vacantes registradas aún en la base de datos. Ejecuta el scraper para comenzar a recopilar datos.")

# Analisis de Skill Gap
st.markdown("---")
st.subheader("🎯 Comparativa de Perfil vs Mercado")

gap = analyze_skill_gap()

col_gap1, col_gap2 = st.columns([1, 2])

with col_gap1:
    st.metric("Coincidencia con el Mercado", f"{gap['match_percentage']}%")
    st.write("**Tecnologías Clave Faltantes:**")
    for skill in gap["missing_skills"]:
        st.markdown(f"- ❌ `{skill}`")

with col_gap2:
    if gap["top_market_skills"]:
        st.write("**Tecnologías Más Solicitadas:**")
        df_skills = pd.DataFrame(list(gap["top_market_skills"].items()), columns=["Tecnología", "Menciones"])
        fig_skills = px.bar(df_skills, x="Tecnología", y="Menciones", color="Menciones")
        st.plotly_chart(fig_skills, use_container_width=True)
