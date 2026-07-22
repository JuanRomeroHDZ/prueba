# test_seed.py
from app.database import get_connection, init_db
from app.utils.parser import classify_job
from datetime import datetime

init_db()
conn = get_connection()
cursor = conn.cursor()

sample_jobs = [
    ("Medtronic", "Sr Network Engineer", "Tijuana", 35000, 45000, "Cisco, OSPF, BGP, Fortinet, VLAN"),
    ("Honeywell", "Cloud Infrastructure Specialist", "Mexicali", 40000, 55000, "Azure, Terraform, Linux, Proxmox, Docker"),
    ("Softtek", "SOC Analyst L2", "Remoto", 30000, 40000, "Wazuh, Splunk, SIEM, EDR, Linux, Python"),
    ("Thermo Fisher Scientific", "Systems Administrator", "Tijuana", 28000, 36000, "Windows Server, Active Directory, VMware, Backup"),
    ("TACNA", "Security & Network Specialist", "Tijuana", 32000, 42000, "Cisco, pfSense, Fortinet, ISO 27001, Wazuh")
]

for emp, puesto, loc, s_min, s_max, tech_desc in sample_jobs:
    parsed = classify_job(puesto, tech_desc)
    s_avg = (s_min + s_max) / 2
    
    cursor.execute('''
        INSERT OR IGNORE INTO jobs 
        (fecha_consulta, empresa, puesto, ubicacion, salario_min, salario_max, salario_promedio, area, tecnologias, fuente, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d"),
        emp, puesto, loc, s_min, s_max, s_avg,
        parsed["area"], parsed["tecnologias"],
        "Test Seed", f"https://example.com/{puesto.lower().replace(' ', '-')}"
    ))

conn.commit()
conn.close()
print("Datos de prueba insertados con éxito.")
