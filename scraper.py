# Requisitos: instale com `pip install selenium beautifulsoup4`
# É necessário ter o ChromeDriver compatível com a versão do Google Chrome instalada

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import json
import os

# === CONFIGURAÇÕES ===
BUSCA_URL = "https://portal.gupy.io/job-search/term=jovem%20aprendiz"
HEADLESS = True  # Coloque False se quiser ver o navegador
LIMITAR_VAGAS = 10  # Use None para pegar todas
SAIDA_ARQUIVO = "vagas_gupy.json"

# === FUNÇÕES ===
def iniciar_driver():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Caminho do ChromeDriver (GitHub Actions já tem no PATH)
    servico = Service()
    driver = webdriver.Chrome(service=servico, options=chrome_options)
    return driver

def get_links_com_selenium(driver):
    print("[INFO] Acessando página de busca...")
    driver.get(BUSCA_URL)
    time.sleep(5)  # Espera o JS carregar

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    vagas = []
    for a in soup.select('a[href*="/job/"]'):
        href = a['href']
        if href.startswith("https") and href not in vagas:
            vagas.append(href)
    print(f"[INFO] {len(vagas)} vagas encontradas")
    return vagas[:LIMITAR_VAGAS] if LIMITAR_VAGAS else vagas

def get_logo_empresa(driver, dominio):
    try:
        driver.get(dominio)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        div_logo = soup.find('div', class_='sc-e9dd4d1-4')
        if div_logo and div_logo.find('img'):
            return div_logo.find('img')['src']
    except Exception as e:
        print(f"[ERRO] Logo não encontrada em {dominio}: {e}")
    return ""

def get_dados_vaga(driver, link):
    try:
        driver.get(link)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        titulo = soup.find("h1")
        titulo = titulo.text.strip() if titulo else "Sem título"

        local = ""
        local_div = soup.find("span", string=lambda t: t and ("Remoto" in t or "," in t))
        if local_div:
            local = local_div.text.strip()

        parsed = urlparse(link)
        dominio_empresa = f"{parsed.scheme}://{parsed.netloc}"
        logo = get_logo_empresa(driver, dominio_empresa)

        return {
            "titulo": titulo,
            "local": local,
            "empresa": parsed.netloc.replace(".gupy.io", ""),
            "link": link,
            "logo": logo
        }
    except Exception as e:
        print(f"[ERRO] Falha ao processar vaga {link}: {e}")
        return None

# === EXECUÇÃO PRINCIPAL ===
def main():
    driver = iniciar_driver()
    vagas = get_links_com_selenium(driver)
    resultado = []

    for idx, link in enumerate(vagas):
        print(f"[INFO] Processando vaga {idx+1}/{len(vagas)}")
        dados = get_dados_vaga(driver, link)
        if dados:
            resultado.append(dados)
        time.sleep(1)

    driver.quit()

    with open(SAIDA_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(resultado)} vagas salvas em {SAIDA_ARQUIVO}")

if __name__ == "__main__":
    main()
