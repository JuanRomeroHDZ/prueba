import re

CATEGORIES = {
    "Networking": [
        "cisco", "vlan", "ospf", "bgp", "switching", "routing", 
        "firewall", "pfsense", "fortinet", "sd-wan", "ccna", "ccnp"
    ],
    "Infrastructure": [
        "vmware", "hyper-v", "proxmox", "linux", "debian", "ubuntu", 
        "windows server", "active directory", "backup", "storage", "truenas", "san", "nas"
    ],
    "Cloud": [
        "azure", "aws", "gcp", "kubernetes", "docker", "terraform", "ansible", "devops"
    ],
    "Cybersecurity": [
        "siem", "soc", "edr", "ids", "ips", "wazuh", "splunk", 
        "vulnerability", "iso 27001", "cissp", "compTIA security+"
    ]
}

def classify_job(puesto: str, descripcion: str) -> dict:
    text = f"{puesto} {descripcion}".lower()
    
    detected_categories = []
    detected_techs = set()
    
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                detected_categories.append(category)
                detected_techs.add(kw.capitalize())
                
    main_area = detected_categories[0] if detected_categories else "General IT"
    
    return {
        "area": main_area,
        "tecnologias": ", ".join(detected_techs)
    }
