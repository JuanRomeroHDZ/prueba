import re
import hashlib

CAREER_PATH_MAP = {
    "Networking": "Infraestructura Base",
    "Infrastructure & Systems": "Infraestructura Base",
    "Cloud & DevOps": "Cloud & Automatización",
    "Cybersecurity & SOC": "Seguridad"
}

HIGH_PRIORITY_COMPANIES = [
    "enteracloud", "nerium", "schneider electric", "thermo fisher", 
    "kio networks", "sonda", "scitum", "alestra", "telmex", "megacable", "totalplay"
]

MEDIUM_PRIORITY_COMPANIES = [
    "jabil", "flex", "honeywell", "medtronic", "skyworks", "bd", "becton dickinson",
    "integer", "bose", "sony", "stryker", "insulet", "teradyne", "eaton", 
    "nova system", "softtek", "ntt data", "t-systems", "ibm", "oracle", "microsoft", 
    "cisco", "fortinet", "palo alto", "dell", "vmware", "red hat", "aws"
]

IT_KEYWORDS = [
    "redes", "network", "networking", "network engineer", "network administrator", 
    "network analyst", "noc engineer", "lan engineer", "wan engineer", "cisco engineer",
    "cisco", "vlan", "ospf", "bgp", "switching", "routing", "firewall", "pfsense", "fortinet",
    "infraestructura", "infrastructure", "systems engineer", "system administrator", 
    "sysadmin", "linux administrator", "windows administrator", "server administrator", 
    "data center engineer", "soporte it", "it support", "virtualizacion", "proxmox", "vmware",
    "linux", "debian", "ubuntu", "windows server", "active directory", "backup", "storage", "truenas",
    "cloud", "cloud engineer", "azure administrator", "aws engineer", "cloud support engineer", 
    "devops engineer", "platform engineer", "devsecops", "azure", "aws", "gcp", "kubernetes", "docker", "terraform",
    "seguridad", "ciberseguridad", "cybersecurity", "soc analyst", "security analyst", 
    "cybersecurity analyst", "security engineer", "network security engineer", 
    "vulnerability analyst", "incident response analyst", "siem", "wazuh", "splunk", "edr"
]

EXCLUDE_KEYWORDS = [
    "redes sociales", "social media", "marketing", "mercadotecnia", "publicidad",
    "hotel", "hotelería", "camarero", "camarera", "limpieza", "intendencia",
    "recepcionista", "mesero", "cajero", "chofer", "ventas", "ejecutivo de ventas",
    "sistemas de calidad", "gestión de calidad", "iso 9001", "recursos humanos",
    "contabilidad", "contador", "auxiliar administrativo", "mantenimiento industrial",
    "mecanico", "electromecanico", "enfermero", "medico"
]

def generate_fingerprint(empresa: str, puesto: str, ubicacion: str) -> str:
    """
    Genera un hash SHA-256 único normalizando empresa, puesto y ubicación
    para evitar duplicados entre distintas fuentes.
    """
    clean_empresa = re.sub(r'[^a-zA-Z0-9]', '', empresa.lower())
    clean_puesto = re.sub(r'[^a-zA-Z0-9]', '', puesto.lower())
    clean_loc = "tijuana" if "tijuana" in ubicacion.lower() or "b.c" in ubicacion.lower() else "remoto"
    
    raw_str = f"{clean_empresa}|{clean_puesto}|{clean_loc}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()


def get_company_priority(company_name: str) -> str:
    comp = company_name.lower()
    if any(p in comp for p in HIGH_PRIORITY_COMPANIES):
        return "🟢 Alta"
    elif any(p in comp for p in MEDIUM_PRIORITY_COMPANIES):
        return "🟡 Media"
    return "⚪ Normal"


def is_tijuana_or_remote(location_str: str, title_str: str = "") -> bool:
    text = f"{location_str} {title_str}".lower()
    if any(r in text for r in ["remoto", "remote", "home office", "work from home"]):
        return True
    excluded = ["guadalajara", "monterrey", "ciudad de méxico", "cdmx", "querétaro", "puebla", "estado de méxico"]
    if any(city in text for city in excluded) and "tijuana" not in text:
        return False
    return any(kw in text for kw in ["tijuana", "b.c", "b.c.", "baja california"])


def is_valid_it_job(puesto: str, descripcion: str = "") -> bool:
    full_text = f"{puesto} {descripcion}".lower()
    if any(ex in full_text for ex in EXCLUDE_KEYWORDS):
        return False
    return any(re.search(r'\b' + re.escape(kw) + r'\b', full_text) for kw in IT_KEYWORDS)


def extract_salary_from_text(text: str) -> str:
    if not text:
        return ""
    match_range = re.search(r'(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*k)?\s*(?:a|-|–)\s*\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*k)?)', text, re.IGNORECASE)
    if match_range:
        return match_range.group(1)
    match_single = re.search(r'(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:\s*k)?|\d{1,3}(?:,\d{3})+\s*mxn)', text, re.IGNORECASE)
    if match_single:
        return match_single.group(1)
    return ""


def parse_salary(salary_str: str) -> tuple[float, float, float]:
    if not salary_str or any(kw in salary_str.lower() for kw in ["no especificado", "salario no mostrado", "confidencial"]):
        return None, None, None

    normalized = re.sub(r'(\d+)\s*k\b', lambda m: str(int(m.group(1)) * 1000), salary_str, flags=re.IGNORECASE)
    clean_text = normalized.replace(",", "").replace("$", "")
    numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', clean_text)]
    valid_nums = [n for n in numbers if 3000 <= n <= 350000]

    if len(valid_nums) >= 2:
        s_min, s_max = min(valid_nums[:2]), max(valid_nums[:2])
        if "quincenal" in salary_str.lower():
            s_min, s_max = s_min * 2, s_max * 2
        elif s_min > 120000:
            s_min, s_max = round(s_min / 12, 2), round(s_max / 12, 2)
        return s_min, s_max, round((s_min + s_max) / 2, 2)
    elif len(valid_nums) == 1:
        val = valid_nums[0]
        if "quincenal" in salary_str.lower():
            val = val * 2
        elif val > 120000:
            val = round(val / 12, 2)
        return val, val, val

    return None, None, None


def extract_experience(text: str) -> str:
    text_lower = text.lower()
    match_years = re.search(r'(\d+)\s*(?:a|-|–)?\s*(\d+)?\s*(?:años?|years?)\b', text_lower)
    if match_years:
        min_y, max_y = match_years.group(1), match_years.group(2)
        return f"{min_y}-{max_y} años" if max_y else f"{min_y}+ años"
    if "junior" in text_lower or "trainee" in text_lower or "entry" in text_lower:
        return "0-1 año (Junior)"
    elif "senior" in text_lower or "sr" in text_lower or "lead" in text_lower:
        return "5+ años (Senior)"
    return "1-3 años"


def extract_english(text: str) -> str:
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["inglés avanzado", "english advanced", "bilingüe", "bilingual", "90%", "80%"]):
        return "Avanzado / Bilingüe"
    elif any(kw in text_lower for kw in ["inglés conversacional", "conversational english", "inglés intermedio", "70%"]):
        return "Intermedio"
    elif "inglés" in text_lower or "english" in text_lower:
        return "Requerido"
    return "No especificado"


def extract_certifications(text: str) -> str:
    certs = ["CCNA", "CCNP", "NSE", "Security+", "Network+", "CISSP", "CEH", "AWS", "Azure", "ITIL"]
    found = [c for c in certs if re.search(r'\b' + re.escape(c) + r'\b', text, re.IGNORECASE)]
    return ", ".join(found) if found else "Ninguna especificada"


def detect_modality(text: str) -> str:
    text_lower = text.lower()
    if "remoto" in text_lower or "remote" in text_lower or "home office" in text_lower:
        return "Remoto"
    elif "híbrido" in text_lower or "hybrid" in text_lower:
        return "Híbrido"
    return "Presencial"


def classify_job(puesto: str, descripcion: str) -> dict:
    text = f"{puesto} {descripcion}".lower()
    
    # Detección profunda de tecnologías específicas
    known_techs = [
        "Cisco", "Linux", "Proxmox", "TrueNAS", "Wazuh", "pfSense", "Azure", "AWS", 
        "VMware", "Docker", "Kubernetes", "Fortinet", "Splunk", "Python", "Active Directory"
    ]
    detected = [t for t in known_techs if re.search(r'\b' + re.escape(t) + r'\b', text, re.IGNORECASE)]
    
    if any(kw in text for kw in ["soc", "siem", "ciberseguridad", "security", "wazuh", "vulnerability"]):
        area = "Cybersecurity & SOC"
    elif any(kw in text for kw in ["cloud", "aws", "azure", "devops", "kubernetes", "docker", "terraform"]):
        area = "Cloud & DevOps"
    elif any(kw in text for kw in ["cisco", "redes", "network", "vlan", "bgp", "noc", "pfsense", "fortinet"]):
        area = "Networking"
    else:
        area = "Infrastructure & Systems"
        
    career_path = CAREER_PATH_MAP.get(area, "Infraestructura Base")
    
    return {
        "area": area,
        "career_path": career_path,
        "tecnologias": ", ".join(detected) if detected else "Infraestructura TI"
    }
