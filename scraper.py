import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

def get_links_de_vagas():
    url = "https://portal.gupy.io/job-search/term=jovem%20aprendiz"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    vagas = []
    for a in soup.select('a[href^="https://"]'):
        link = a['href']
        if '/job/' in link:
            vagas.append(link)
    return list(set(vagas))  # remove duplicatas

def get_dados_vaga(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, "html.parser")

    # Título da vaga
    titulo = soup.find("h1")
    titulo = titulo.text.strip() if titulo else "Sem título"

    # Local da vaga (exemplo heurístico)
    local = soup.find(string=lambda t: "Local" in t or "Remoto" in t)
    if local:
        local = local.strip()
    else:
        local = "Local não identificado"

    # Domínio da empresa
    parsed = urlparse(link)
    dominio_empresa = f"{parsed.scheme}://{parsed.netloc}"

    # Logo da empresa
    logo = get_logo_empresa(dominio_empresa)

    return {
        "titulo": titulo,
        "local": local,
        "link": link,
        "empresa": parsed.netloc.replace(".gupy.io", ""),
        "logo": logo
    }

def get_logo_empresa(dominio):
    try:
        html = requests.get(dominio).text
        soup = BeautifulSoup(html, "html.parser")
        div_logo = soup.find('div', class_='sc-e9dd4d1-4')
        if div_logo and div_logo.find('img'):
            return div_logo.find('img')['src']
    except:
        pass
    return "Logo não encontrada"

# Execução
vagas = get_links_de_vagas()
print(f"Encontradas {len(vagas)} vagas.")

for link in vagas[:5]:  # limitar para testes
    dados = get_dados_vaga(link)
    print(dados)
    time.sleep(1.5)  # evitar sobrecarregar o site
    vagas = get_links_de_vagas()
print(f"[DEBUG] Total de links capturados: {len(vagas)}")
print(vagas)

