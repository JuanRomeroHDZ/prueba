import requests
from bs4 import BeautifulSoup
import time
import random

# Definir un User-Agent realista para evitar bloqueos básicos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_occ_jobs(keyword="Redes", max_pages=2):
    """
    Extrae vacantes de OCC Mundial según la palabra clave enviada.
    """
    jobs_found = []
    
    for page in range(1, max_pages + 1):
        url = f"https://www.occ.com.mx/empleos/en-mexico-y-el-mundo/para-{keyword}/?page={page}"
        print(f"🔎 Buscando en OCC: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Error {response.status_code} al consultar la página {page}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ubicar tarjetas de empleo (los selectores de OCC varían con el tiempo)
            job_cards = soup.find_all('div', class_=lambda c: c and 'job-card' in c.lower()) if soup else []
            
            for card in job_cards:
                title_elem = card.find('h2') or card.find('a')
                company_elem = card.find('span', class_=lambda c: c and 'company' in c.lower())
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True) if company_elem else "Empresa no especificada"
                    
                    jobs_found.append({
                        "puesto": title,
                        "empresa": company,
                        "fuente": "OCC Mundial",
                        "ubicacion": "México"
                    })
                    
            # Pausa respetuosa para no saturar el servidor objetivo
            time.sleep(random.uniform(1.5, 3.0))
            
        except Exception as e:
            print(f"❌ Error durante el scraping en OCC: {e}")
            
    return jobs_found

if __name__ == "__main__":
    results = scrape_occ_jobs("Infraestructura", max_pages=1)
    print(f"✅ Se encontraron {len(results)} empleos.")
