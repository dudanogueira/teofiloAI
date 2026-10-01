"""Fixtures do pytest: o site de teste servido localmente e o navegador.

Variáveis de ambiente opcionais:
    NAVEGADOR = chrome | edge | firefox | safari   (padrão: edge no Windows, chrome no resto)
    HEADLESS  = 1 | 0                              (padrão: 1, sem janela)
"""
import functools
import http.server
import os
import platform
import threading
from pathlib import Path

import pytest
from selenium import webdriver

SITE = Path(__file__).resolve().parent.parent / "site_teste"


def abrir_navegador(nome: str, headless: bool) -> webdriver.Remote:
    nome = nome.lower()
    if nome == "chrome":
        opcoes = webdriver.ChromeOptions()
        if headless:
            opcoes.add_argument("--headless=new")
        return webdriver.Chrome(options=opcoes)
    if nome == "edge":
        opcoes = webdriver.EdgeOptions()
        if headless:
            opcoes.add_argument("--headless=new")
        return webdriver.Edge(options=opcoes)
    if nome == "firefox":
        opcoes = webdriver.FirefoxOptions()
        if headless:
            opcoes.add_argument("-headless")
        return webdriver.Firefox(options=opcoes)
    if nome == "safari":  # não tem modo headless
        return webdriver.Safari()
    raise ValueError(f"Navegador desconhecido: {nome}")


@pytest.fixture(scope="session")
def url_site():
    """Sobe um servidor HTTP numa porta livre servindo site_teste/ e devolve a URL."""
    class Silencioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # não imprime uma linha por requisição
            pass

    handler = functools.partial(Silencioso, directory=str(SITE))
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)  # porta 0 = o SO escolhe
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_port}/index.html"
    servidor.shutdown()


@pytest.fixture(scope="session")
def driver():
    padrao = "edge" if platform.system() == "Windows" else "chrome"
    navegador = abrir_navegador(
        os.getenv("NAVEGADOR", padrao),
        headless=os.getenv("HEADLESS", "1") == "1",
    )
    yield navegador
    navegador.quit()
