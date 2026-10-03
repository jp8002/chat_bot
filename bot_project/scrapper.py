from urllib.parse import urljoin
import time
import requests
from bs4 import BeautifulSoup
from preprocessing import simple_cleaning
from rich.progress import Progress



class Scrapper:

    def __init__(self, user_agent="ProjetoFatec"):
        """Inicializa a sessão HTTP padrão para todas as requisições."""
        self.sessao = requests.Session()
        self.sessao.headers.update({"User-Agent": user_agent})

    def _salvar_paragrafos(self, soup, filename="base.txt"):
        """Método auxiliar interno para extrair parágrafos e salvar no arquivo."""
        paragrafos = soup.find_all("p")
        if not paragrafos:
            return

        with open(filename, "a", encoding="utf-8") as f:
            for p in paragrafos:
                cleaned_text = simple_cleaning(p.get_text())
                if cleaned_text.strip():
                    f.write(cleaned_text + "\n")

    def scrap(self, url, filename="base.txt"):
        """Faz a requisição de uma URL e salva o conteúdo de seus parágrafos."""
        try:
            resposta = self.sessao.get(url, timeout=(3, 20))
            resposta.raise_for_status()

            soup = BeautifulSoup(resposta.text, "html.parser")
            self._salvar_paragrafos(soup, filename=filename)

        except requests.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")

    def findLink(self, start_url, filename="base.txt", delay=5):
        PAGINAS = 50
        """Mapeia a página inicial, salva seus parágrafos e segue os links."""
        print(f"Iniciando raspagem em: {start_url}")

        try:
            resposta = self.sessao.get(start_url, timeout=(3, 20))
            resposta.raise_for_status()
        except requests.RequestException as e:
            print(f"Falha ao carregar a URL inicial {start_url}: {e}")
            return

        soup = BeautifulSoup(resposta.text, "html.parser")
        self._salvar_paragrafos(soup, filename=filename)

       # UTILIZA SELETOR CSS: Busca apenas tags <a> com href que estão dentro de tags <p>
        links = soup.select("p a[href]")
        
        with Progress() as p:
                t = p.add_task("Tokenizando a base...", total=100)
                while not p.finished:
                    for count, tag in enumerate(links, start=1):
                        p.update(t, advance=100/PAGINAS)
                        
                        time.sleep(delay)
                        
                        if count > PAGINAS:
                            return
                        
                        raw_href = tag["href"].strip()

                        # Ignora âncoras internas, links JS e mailto
                        if (
                            raw_href.startswith("#")
                            or raw_href.startswith("javascript:")
                            or raw_href.startswith("mailto:")
                        ):
                            continue

                        full_url = urljoin(start_url, raw_href)

                        self.scrap(full_url, filename=filename)