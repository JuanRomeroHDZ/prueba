import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from app.utils.parser import is_tijuana_or_remote, extract_salary_from_text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7"
}

def prioritize_jobs_with_salary(jobs_list):
    with_salary = []
    without_salary = []
    
    for j in jobs_list:
        raw_sal = j.get("salario_raw", "").strip()
        if raw_sal and raw_sal.lower() not in ["no especificado", "salario no mostrado", "confidencial", ""]:
            with_salary.append(j)
        else:
            without_salary.append(j)
            
    print(f"📊 Extracción final: {len(with_salary)} vacantes CON salario detectado | {len(without_salary)} sin sueldo explícito.")
    return with_salary + without_salary


def scrape_talenteca_tijuana(keyword="Network Engineer"):
    print(f"🔎 [Talenteca] Buscando '{keyword}' en Tijuana...")
    url = f"https://www.talenteca.com/mexico/empleo/{keyword.lower().replace(' ', '-')}/en-tijuana-bc"
    jobs = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_=lambda c: c and 'panel-body' in c) or soup.find_all('article')
            for card in cards[:10]:
                title_elem = card.find(['h3', 'h2', 'a'])
                comp_elem = card.find(class_=lambda c: c and 'company' in c.lower())
                if title_elem:
                    jobs.append({
                        "puesto": title_elem.get_text(strip=True),
                        "empresa": comp_elem.get_text(strip=True) if comp_elem else "Empresa TI",
                        "ubicacion": "Tijuana, B.C.",
                        "salario_raw": extract_salary_from_text(card.get_text(" ", strip=True)),
                        "fuente": "Talenteca",
                        "url": url
                    })
    except Exception as e:
        print(f"⚠️ Error en Talenteca: {e}")
    return jobs


def scrape_jooble_tijuana(keyword="Infrastructure"):
    print(f"🔎 [Jooble] Buscando '{keyword}' en Tijuana...")
    url = f"https://mx.jooble.org/resultado/{keyword}/Tijuana%2C%20B.C."
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(extra_http_headers=HEADERS)
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            time.sleep(2)
            cards = page.query_selector_all('article')
            for card in cards[:10]:
                title_elem = card.query_selector('h2') or card.query_selector('a')
                if title_elem:
                    jobs.append({
                        "puesto": title_elem.inner_text().strip(),
                        "empresa": "Empresa Verificada Jooble",
                        "ubicacion": "Tijuana, B.C.",
                        "salario_raw": extract_salary_from_text(card.inner_text()),
                        "fuente": "Jooble MX",
                        "url": url
                    })
        except Exception as e:
            print(f"⚠️ Error en Jooble: {e}")
        browser.close()
    return jobs


def scrape_remote_co(keyword="DevOps"):
    print(f"🔎 [Remote.co] Buscando vacantes remotas de '{keyword}'...")
    url = f"https://remote.co/remote-jobs/search/?search_keywords={keyword}"
    jobs = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('a', class_=lambda c: c and 'card' in c.lower())
            for card in cards[:5]:
                title_elem = card.find('p', class_=lambda c: c and 'font-weight-bold' in c) or card.find('span')
                if title_elem:
                    jobs.append({
                        "puesto": title_elem.get_text(strip=True),
                        "empresa": "Empresa Internacional (Remoto)",
                        "ubicacion": "100% Remoto",
                        "salario_raw": "",
                        "fuente": "Remote.co",
                        "url": "https://remote.co" + card.get('href', '')
                    })
    except Exception as e:
        print(f"⚠️ Error en Remote.co: {e}")
    return jobs


def scrape_empleonuevo_tijuana(keyword="Redes"):
    print(f"🔎 [Empleo Nuevo] Buscando '{keyword}' en Tijuana...")
    url = f"https://www.empleonuevo.com/empleos?q={keyword}&l=Tijuana"
    jobs = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_=lambda c: c and 'job-card' in c.lower()) or soup.find_all('article')
            for card in cards[:10]:
                card_text = card.get_text(" ", strip=True)
                title_elem = card.find(['h2', 'h3', 'a'])
                comp_elem = card.find(class_=lambda c: c and ('company' in c.lower() or 'empresa' in c.lower()))
                loc_elem = card.find(class_=lambda c: c and ('location' in c.lower() or 'ubicacion' in c.lower()))
                salary_elem = card.find(class_=lambda c: c and ('salary' in c.lower() or 'sueldo' in c.lower()))
                
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    location = loc_elem.get_text(strip=True) if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        company = comp_elem.get_text(strip=True) if comp_elem else "Empresa Local Tijuana"
                        salary = salary_elem.get_text(strip=True) if salary_elem else extract_salary_from_text(card_text)
                        href = title_elem.get('href', '') if title_elem.name == 'a' else ''
                        
                        jobs.append({
                            "puesto": title,
                            "empresa": company,
                            "ubicacion": location,
                            "salario_raw": salary,
                            "fuente": "Empleo Nuevo",
                            "url": f"https://www.empleonuevo.com{href}" if href.startswith('/') else href or url
                        })
    except Exception as e:
        print(f"⚠️ Error en Empleo Nuevo: {e}")
    return jobs


def scrape_indeed_tijuana(keyword="Redes"):
    print(f"🔎 [Indeed] Buscando '{keyword}' en Tijuana...")
    url = f"https://mx.indeed.com/jobs?q={keyword}&l=Tijuana%2C+BC"
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=HEADERS["User-Agent"], locale="es-MX")
        page = context.new_page()
        try:
            page.goto(url, timeout=25000, wait_until="domcontentloaded")
            time.sleep(2)
            cards = page.query_selector_all('div.job_seen_beacon') or page.query_selector_all('td.resultContent')
            
            for card in cards[:10]:
                card_text = card.inner_text()
                title_elem = card.query_selector('h2.jobTitle span') or card.query_selector('a[id^="job_"]')
                comp_elem = card.query_selector('span[data-testid="company-name"]')
                loc_elem = card.query_selector('div[data-testid="text-location"]')
                salary_elem = card.query_selector('div.metadata.salary-snippet-container') or card.query_selector('div[data-testid="attribute_snippet"]')
                link_elem = card.query_selector('a[id^="job_"]')
                
                if title_elem:
                    title = title_elem.inner_text().strip()
                    location = loc_elem.inner_text().strip() if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        company = comp_elem.inner_text().strip() if comp_elem else "Confidencial"
                        salary = salary_elem.inner_text().strip() if salary_elem else extract_salary_from_text(card_text)
                        job_key = link_elem.get_attribute('data-jk') if link_elem else None
                        
                        jobs.append({
                            "puesto": title,
                            "empresa": company,
                            "ubicacion": location,
                            "salario_raw": salary,
                            "fuente": "Indeed",
                            "url": f"https://mx.indeed.com/viewjob?jk={job_key}" if job_key else url
                        })
        except Exception as e:
            print(f"⚠️ Error en Indeed: {e}")
        browser.close()
    return jobs


def scrape_glassdoor_tijuana(keyword="Redes"):
    print(f"🔎 [Glassdoor] Buscando '{keyword}' en Tijuana...")
    url = f"https://www.glassdoor.com.mx/Empleo/tijuana-{keyword.lower()}-empleos-SRCH_IL.0,7_IC2560378.htm"
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=HEADERS["User-Agent"], locale="es-MX")
        page = context.new_page()
        try:
            page.goto(url, timeout=25000, wait_until="domcontentloaded")
            time.sleep(2)
            cards = page.query_selector_all('li[data-test="jobListing"]') or page.query_selector_all('div[class*="jobCard"]')
            
            for card in cards[:10]:
                card_text = card.inner_text()
                title_elem = card.query_selector('a[data-test="job-title"]')
                comp_elem = card.query_selector('div[class*="EmployerName"]')
                loc_elem = card.query_selector('span[data-test="emp-location"]')
                salary_elem = card.query_selector('span[data-test="detailSalary"]')
                
                if title_elem:
                    title = title_elem.inner_text().strip()
                    location = loc_elem.inner_text().strip() if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        company = comp_elem.inner_text().strip() if comp_elem else "Confidencial"
                        salary = salary_elem.inner_text().strip() if salary_elem else extract_salary_from_text(card_text)
                        href = title_elem.get_attribute('href') or ''
                        
                        jobs.append({
                            "puesto": title,
                            "empresa": company,
                            "ubicacion": location,
                            "salario_raw": salary,
                            "fuente": "Glassdoor",
                            "url": f"https://www.glassdoor.com.mx{href}" if href.startswith('/') else href or url
                        })
        except Exception as e:
            print(f"⚠️ Error en Glassdoor: {e}")
        browser.close()
    return jobs


def scrape_linkedin_tijuana(keyword="Redes", limit=10):
    print(f"🔎 [LinkedIn] Buscando '{keyword}' en Tijuana...")
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keyword}&location=Tijuana%2C%20Baja%20California%2C%20Mexico&start=0"
    jobs = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('li')
            
            for card in cards[:limit]:
                card_text = card.get_text(" ", strip=True)
                title_elem = card.find('h3', class_=lambda c: c and 'base-search-card__title' in c)
                comp_elem = card.find('h4', class_=lambda c: c and 'base-search-card__subtitle' in c)
                loc_elem = card.find('span', class_=lambda c: c and 'job-search-card__location' in c)
                link_elem = card.find('a', class_=lambda c: c and 'base-card__full-link' in c)
                
                if title_elem and comp_elem:
                    title = title_elem.get_text(strip=True)
                    location = loc_elem.get_text(strip=True) if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        jobs.append({
                            "puesto": title,
                            "empresa": comp_elem.get_text(strip=True),
                            "ubicacion": location,
                            "salario_raw": extract_salary_from_text(card_text),
                            "fuente": "LinkedIn",
                            "url": link_elem['href'] if link_elem and 'href' in link_elem.attrs else "https://www.linkedin.com/jobs"
                        })
    except Exception as e:
        print(f"⚠️ Error en LinkedIn: {e}")
    return jobs


def scrape_computrabajo_tijuana(keyword="redes"):
    print(f"🔎 [Computrabajo] Buscando '{keyword}' en Tijuana...")
    formatted_kw = keyword.lower().replace(" ", "-")
    url = f"https://mx.computrabajo.com/trabajo-de-{formatted_kw}-en-tijuana"
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(extra_http_headers=HEADERS)
        try:
            page.goto(url, timeout=25000, wait_until="domcontentloaded")
            time.sleep(2)
            cards = page.query_selector_all('article.box_offer')
            
            for card in cards:
                card_text = card.inner_text()
                title_elem = card.query_selector('h2 a') or card.query_selector('a.js-o-link')
                comp_elem = card.query_selector('p.fc_base') or card.query_selector('a[href*="/empresas/"]')
                loc_elem = card.query_selector('p.fs14') or card.query_selector('span.mr10')
                salary_elem = card.query_selector('span.tc_base') or card.query_selector('span[class*="salary"]')
                
                if title_elem:
                    title = title_elem.inner_text().strip()
                    location = loc_elem.inner_text().strip() if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        company = comp_elem.inner_text().strip() if comp_elem else "Empresa Confidencial"
                        salary = salary_elem.inner_text().strip() if salary_elem else extract_salary_from_text(card_text)
                        rel_link = title_elem.get_attribute('href') or ""
                        
                        jobs.append({
                            "puesto": title,
                            "empresa": company,
                            "ubicacion": location,
                            "salario_raw": salary,
                            "fuente": "Computrabajo",
                            "url": f"https://mx.computrabajo.com{rel_link}" if rel_link.startswith('/') else rel_link
                        })
        except Exception as e:
            print(f"⚠️ Error en Computrabajo: {e}")
        browser.close()
    return jobs


def scrape_occ_tijuana(keyword="Redes"):
    print(f"🔎 [OCC Mundial] Buscando '{keyword}' en Tijuana...")
    url = f"https://www.occ.com.mx/empleos/en-baja-california/en-tijuana/para-{keyword}/"
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(extra_http_headers=HEADERS)
        try:
            page.goto(url, timeout=25000, wait_until="domcontentloaded")
            time.sleep(2.5)
            cards = page.query_selector_all('div[id^="jobcard-"]')
            
            for card in cards:
                card_text = card.inner_text()
                title_elem = card.query_selector('h2') or card.query_selector('a')
                comp_elem = card.query_selector('span[class*="company"]')
                loc_elem = card.query_selector('span[class*="location"]')
                salary_elem = card.query_selector('span[class*="salary"]')
                link_elem = card.query_selector('a[href*="/empleo/oferta/"]')
                
                if title_elem:
                    title = title_elem.inner_text().strip()
                    location = loc_elem.inner_text().strip() if loc_elem else "Tijuana, B.C."
                    
                    if is_tijuana_or_remote(location, title):
                        company = comp_elem.inner_text().strip() if comp_elem else "Confidencial"
                        salary = salary_elem.inner_text().strip() if salary_elem else extract_salary_from_text(card_text)
                        rel_link = link_elem.get_attribute("href") if link_elem else ""
                        
                        jobs.append({
                            "puesto": title,
                            "empresa": company,
                            "ubicacion": location,
                            "salario_raw": salary,
                            "fuente": "OCC Mundial",
                            "url": f"https://www.occ.com.mx{rel_link}" if rel_link.startswith('/') else rel_link
                        })
        except Exception as e:
            print(f"⚠️ Error en OCC Tijuana: {e}")
        browser.close()
    return jobs
