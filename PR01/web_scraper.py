import requests
from bs4 import BeautifulSoup
import time
import re
import unicodedata

def limpar_texto(texto):
    if not texto: return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    return re.sub(r'\s+', ' ', texto).strip()

def converter_preco_float(valor_str):
    try:
        limpo = re.sub(r'[^\d,]', '', valor_str)
        limpo = limpo.replace(',', '.')
        return float(limpo)
    except:
        return 0.0

def formatar_moeda_br(valor_float):
    try:
        return f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

def validar_produto(soup, url):
    title = soup.find('h1', class_='product_title')
    if not title or not title.get_text().strip():
        return False, "Sem Título"
    price_tag = soup.find('p', class_='price')
    if not price_tag:
        return False, "Sem Container de Preço"
    price_text = limpar_texto(price_tag.get_text())
    if not price_text:
        return False, "Preço Vazio"
    return True, "OK"

def extrair_detalhes_produto(product_url, headers):
    for tentativa in range(3):
        try:
            response = requests.get(product_url, headers=headers, timeout=20)
            if response.status_code != 200:
                time.sleep(1)
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            is_valid, motivo = validar_produto(soup, product_url)
            if not is_valid:
                print(f"   [IGNORADO] {motivo} -> {product_url}")
                return None
            details = {'link': product_url}
            h1 = soup.find('h1', class_='product_title')
            details['nome'] = limpar_texto(h1.text)
            img_url = None
            meta_img = soup.find('meta', property='og:image')
            if meta_img: img_url = meta_img.get('content')
            if not img_url:
                img_tag = soup.find('img', class_='wp-post-image')
                if img_tag: img_url = img_tag.get('data-src') or img_tag.get('src')
            details['imagem_url'] = img_url if img_url else ''
            details['preco_vista'] = '0,00'
            details['preco_prazo'] = ''
            valor_vista_float = 0.0
            price_div = soup.find('p', class_='price')
            if price_div:
                txt = limpar_texto(price_div.get_text())
                vals = re.findall(r'R\$\s*([\d\.,]+)', txt)
                if vals: 
                    str_valor = vals[-1]
                    details['preco_vista'] = str_valor
                    valor_vista_float = converter_preco_float(str_valor)
            product_container = soup.select_one('.product') or soup.body
            full_text_search = limpar_texto(product_container.get_text(separator=' ')) if product_container else ""
            details['cod'] = ""
            match_cod = re.search(r'COD\s*[:\.]?\s*(\d+)', full_text_search, re.IGNORECASE)
            if match_cod:
                details['cod'] = match_cod.group(1)
            summary = soup.select_one('.summary')
            summary_text = limpar_texto(summary.get_text(separator=' ')) if summary else full_text_search
            match_text = re.search(r'(10\s*[xX]\s*(?:de)?\s*R\$\s*[\d\.,]+)', summary_text, re.IGNORECASE)
            origem_prazo = "N/A"
            if match_text:
                raw = match_text.group(1)
                details['preco_prazo'] = re.sub(r'\s+', ' ', raw).strip()
                origem_prazo = "TEXTO SITE"
            elif valor_vista_float > 0:
                valor_total_prazo = valor_vista_float * 1.15
                valor_parcela = valor_total_prazo / 10
                details['preco_prazo'] = f"10x R$ {formatar_moeda_br(valor_parcela)}"
                origem_prazo = "CÁLCULO (1.15)"
            else:
                details['preco_prazo'] = "Consultar"
                origem_prazo = "FALHA"
            print("-" * 80)
            print(f"PRODUTO: {details['nome'][:50]}...")
            print(f"   > Cód:   {details['cod']}")
            print(f"   > Vista: R$ {details['preco_vista']}")
            print(f"   > Prazo: {details['preco_prazo']} [{origem_prazo}]")
            print(f"   > Img:   {'OK' if details['imagem_url'] else 'SEM IMAGEM'}")
            print("-" * 80)
            return details
        except Exception as e:
            print(f"   [ERRO CRÍTICO] {product_url}: {e}")
            time.sleep(1)
    return None

def buscar_produtos_site():
    urls_categorias = [
        "https://confortec.com.br/categoria-produto/energia-solar/veiculo-eletrico/",
        "https://confortec.com.br/categoria-produto/energia-solar/",
        "https://confortec.com.br/categoria-produto/componentes-energia-solar/",
        "https://confortec.com.br/categoria-produto/off-grid/",
        "https://confortec.com.br/categoria-produto/on-grid/",
        "https://confortec.com.br/categoria-produto/aquecimento-solar/",
        "https://confortec.com.br/categoria-produto/boiler/",
        "https://confortec.com.br/categoria-produto/coletor-solar/",
        "https://confortec.com.br/categoria-produto/piscina/",
        "https://confortec.com.br/categoria-produto/componentes/",
        "https://confortec.com.br/categoria-produto/aquecedor-de-passagem/",
        "https://confortec.com.br/categoria-produto/aquecedores-komeco-aquecedor-de-passagem/",
        "https://confortec.com.br/categoria-produto/aquecedor-rinnai-aquecedor-de-passagem/",
        "https://confortec.com.br/categoria-produto/kit-conexao/",
        "https://confortec.com.br/categoria-produto/pecas-comeco/",
        "https://confortec.com.br/categoria-produto/pecas-rinnai/",
        "https://confortec.com.br/categoria-produto/bombas-e-pressurizadores/",
        "https://confortec.com.br/categoria-produto/bombas-e-pressurizadores-komeco/",
        "https://confortec.com.br/categoria-produto/bombas-pressurizadores-syllent/",
        "https://confortec.com.br/categoria-produto/bombas-lorenzetti/",
        "https://confortec.com.br/loja/"
    ]
    
    links_unicos = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    print("\n=== INICIANDO RASTREAMENTO VISUAL ===")
    for cat_url in urls_categorias:
        print(f"Categoria: {cat_url}")
        page = 1
        while page <= 20:
            url = f"{cat_url}page/{page}/" if page > 1 else cat_url
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code == 404: break
                soup = BeautifulSoup(resp.content, 'html.parser')
                prods = soup.select('.product a.woocommerce-loop-product__link') or soup.select('.e-loop-item h2 a')
                if not prods: break
                novos = 0
                for a in prods:
                    href = a.get('href')
                    if href and '/produto/' in href and href not in links_unicos:
                        links_unicos.append(href)
                        novos += 1
                if novos == 0: break 
                page += 1
                time.sleep(0.3)
            except: break
    print(f"\n=== PROCESSANDO {len(links_unicos)} PRODUTOS ENCONTRADOS ===\n")
    final = []
    for i, link in enumerate(links_unicos):
        d = extrair_detalhes_produto(link, headers)
        if d: final.append(d)
        time.sleep(0.1)

    return final