import time
import random
from playwright.sync_api import sync_playwright

def scrape_occ_jobs(keyword="Redes", max_pages=1):
    """
    Extrae vacantes reales de OCC Mundial con Playwright incluyendo salarios y modalidades.
    """
    jobs_found = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="es-MX"
        )
        page = context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"https://www.occ.com.mx/empleos/en-mexico-y-el-mundo/para-{keyword}/?page={page_num}"
            print(f"🔎 Extrayendo desde OCC (Página {page_num}): {url}")
            
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)
                
                cards = page.query_selector_all('div[id^="jobcard-"]')
                
                for card in cards:
                    try:
                        title_elem = card.query_selector('h2') or card.query_selector('a')
                        company_elem = card.query_selector('span[class*="company"]')
                        location_elem = card.query_selector('span[class*="location"]')
                        salary_elem = card.query_selector('span[class*="salary"]') or card.query_selector('span:has-text("$")')
                        link_elem = card.query_selector('a[href*="/empleo/oferta/"]')

                        if title_elem:
                            title = title_elem.inner_text().strip()
                            company = company_elem.inner_text().strip() if company_elem else "Confidencial"
                            location = location_elem.inner_text().strip() if location_elem else "México"
                            salary_raw = salary_elem.inner_text().strip() if salary_elem else ""
                            rel_link = link_elem.get_attribute("href") if link_elem else ""
                            full_url = f"https://www.occ.com.mx{rel_link}" if rel_link.startswith('/') else rel_link

                            jobs_found.append({
                                "puesto": title,
                                "empresa": company,
                                "ubicacion": location,
                                "salario_raw": salary_raw,
                                "fuente": "OCC Mundial",
                                "url": full_url,
                                "descripcion": f"{title} - {location} - {salary_raw}"
                            })
                    except Exception:
                        continue

                time.sleep(random.uniform(1.0, 2.0))

            except Exception as e:
                print(f"❌ Error en página {page_num}: {e}")

        browser.close()
        
    return jobs_found
