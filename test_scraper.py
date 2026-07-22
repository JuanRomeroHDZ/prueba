from app.scraper.tijuana import (
    scrape_talenteca_tijuana,
    scrape_jooble_tijuana,
    scrape_remote_co,
    scrape_empleonuevo_tijuana,
    scrape_indeed_tijuana,
    scrape_glassdoor_tijuana,
    scrape_linkedin_tijuana,
    scrape_computrabajo_tijuana,
    scrape_occ_tijuana,
    prioritize_jobs_with_salary
)
from app.utils.parser import (
    classify_job, parse_salary, detect_modality,
    extract_experience, extract_english, extract_certifications,
    is_valid_it_job, get_company_priority, is_tijuana_or_remote
)
from app.database import get_connection, init_db
from datetime import datetime

print("🚀 Recolectando vacantes bilingües de TI en Tijuana & Remoto...\n")

init_db()

keywords = [
    # Redes / NOC
    "Network Engineer", "Network Administrator", "Cisco Engineer", "Redes",
    # Infraestructura / Sysadmin
    "Infrastructure Engineer", "Systems Engineer", "Linux Administrator", "Administrador de Sistemas",
    # Cloud / DevOps
    "Cloud Engineer", "DevOps Engineer", "Azure Administrator", "AWS Engineer",
    # Ciberseguridad / SOC
    "Ciberseguridad", "SOC Analyst", "Security Engineer", "Cybersecurity Analyst",
    # Empresas Clave de Tijuana
    "Schneider Electric", "Thermo Fisher", "Enteracloud", "KIO Networks", "Nerium", "Medtronic", "Jabil"
]

todas_las_vacantes = []

for kw in keywords:
    print(f"--- 🔎 Buscando: {kw.upper()} ---")
    todas_las_vacantes.extend(scrape_talenteca_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_jooble_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_empleonuevo_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_computrabajo_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_occ_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_linkedin_tijuana(keyword=kw, limit=5))
    todas_las_vacantes.extend(scrape_indeed_tijuana(keyword=kw))
    todas_las_vacantes.extend(scrape_glassdoor_tijuana(keyword=kw))
    
    if any(term in kw for term in ["Cloud", "DevOps", "Security"]):
        todas_las_vacantes.extend(scrape_remote_co(keyword=kw))

vacantes_ordenadas = prioritize_jobs_with_salary(todas_las_vacantes)

conn = get_connection()
cursor = conn.cursor()

registrados = 0
descartados = 0
fecha_hoy = datetime.now().strftime("%Y-%m-%d")

for v in vacantes_ordenadas:
    desc_completa = f"{v['puesto']} {v['empresa']} {v.get('salario_raw', '')}"
    
    if not is_valid_it_job(v["puesto"], desc_completa) or not is_tijuana_or_remote(v["ubicacion"], v["puesto"]):
        descartados += 1
        continue

    parsed = classify_job(v["puesto"], desc_completa)
    prioridad = get_company_priority(v["empresa"])
    s_min, s_max, s_avg = parse_salary(v.get("salario_raw", ""))
    modality = detect_modality(v["puesto"])
    exp = extract_experience(desc_completa)
    ingles = extract_english(desc_completa)
    certs = extract_certifications(desc_completa)
    
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs 
            (fecha_consulta, empresa, puesto, prioridad_empresa, career_path, ubicacion, modalidad, 
             salario_min, salario_max, salario_promedio, moneda, area, tecnologias, experiencia, ingles, certificaciones, fuente, url, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fecha_hoy,
            v["empresa"],
            v["puesto"],
            prioridad,
            parsed["career_path"],
            v["ubicacion"],
            modality,
            s_min,
            s_max,
            s_avg,
            "MXN",
            parsed["area"],
            "Especializada TI",
            exp,
            ingles,
            certs,
            v["fuente"],
            v["url"],
            desc_completa
        ))
        if cursor.rowcount > 0:
            registrados += 1
    except Exception:
        continue

conn.commit()
conn.close()

print(f"\n📊 Resumen de recolección para Tijuana:")
print(f"✅ Vacantes reales de TI registradas: {registrados}")
print(f"❌ Ofertas no técnicas / fuera de región descartadas: {descartados}")
