"""Testes automatizados da Loja Teste com Selenium + pytest.

Rode, de dentro de aulas/automacao:   python -m pytest testes -v
Para ver o navegador trabalhando:     HEADLESS=0 python -m pytest testes -v
                         (Windows)    $env:HEADLESS="0"; python -m pytest testes -v
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class LojaTeste:
    """Page Object: reúne em um lugar só COMO interagir com a página.

    Os testes falam a língua do negócio (login, criar_pedido...). Se o HTML
    mudar, só esta classe precisa ser atualizada.
    """

    def __init__(self, driver, url):
        self.driver = driver
        self.url = url
        self.espera = WebDriverWait(driver, timeout=5)

    def abrir(self):
        self.driver.get(self.url)
        return self

    def login(self, usuario, senha):
        self.driver.find_element(By.ID, "usuario").send_keys(usuario)
        self.driver.find_element(By.NAME, "senha").send_keys(senha)
        self.driver.find_element(By.CSS_SELECTOR, "[data-testid=entrar]").click()
        return self

    def mensagem_erro_login(self):
        return self.espera.until(EC.visibility_of_element_located((By.ID, "erro-login"))).text

    def boas_vindas(self):
        return self.espera.until(EC.visibility_of_element_located((By.ID, "boas-vindas"))).text

    def criar_pedido(self, cliente, produto, quantidade=1, entrega="retirada", presente=False):
        self.driver.find_element(By.ID, "cliente").send_keys(cliente)
        Select(self.driver.find_element(By.ID, "produto")).select_by_visible_text(produto)
        campo_qtd = self.driver.find_element(By.ID, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys(str(quantidade))
        self.driver.find_element(By.CSS_SELECTOR, f"input[name=entrega][value={entrega}]").click()
        if presente:
            self.driver.find_element(By.ID, "presente").click()
        self.driver.find_element(By.CSS_SELECTOR, "[data-testid=enviar-pedido]").click()
        return self.driver.find_element(By.ID, "mensagem-pedido").text

    def linhas_da_tabela(self):
        linhas = self.driver.find_elements(By.CSS_SELECTOR, "#tabela-pedidos tbody tr")
        return [[td.text for td in linha.find_elements(By.TAG_NAME, "td")] for linha in linhas]

    def carregar_relatorio(self):
        self.driver.find_element(By.ID, "carregar-relatorio").click()
        return self.espera.until(EC.visibility_of_element_located((By.ID, "relatorio"))).text


@pytest.fixture
def loja(driver, url_site):
    return LojaTeste(driver, url_site).abrir()  # recarregar a página zera o estado


def test_titulo_da_pagina(loja):
    assert "Loja Teste" in loja.driver.title


def test_login_com_senha_errada_mostra_erro(loja):
    loja.login("aluno", "errada")
    assert loja.mensagem_erro_login() == "Usuário ou senha inválidos."


def test_login_correto_mostra_boas_vindas(loja):
    loja.login("aluno", "selenium123")
    assert loja.boas_vindas() == "Bem-vindo(a), aluno!"


@pytest.mark.parametrize(
    "produto, quantidade, entrega",
    [("Café especial", 1, "retirada"), ("Queijo minas", 5, "casa")],
    ids=["cafe-retirada", "queijo-casa"],
)
def test_criar_pedido_entra_na_tabela(loja, produto, quantidade, entrega):
    loja.login("aluno", "selenium123")
    mensagem = loja.criar_pedido("Duda", produto, quantidade, entrega)

    assert mensagem.startswith("Pedido registrado")
    assert loja.linhas_da_tabela()[-1] == ["Duda", produto, str(quantidade), entrega]


def test_pedido_sem_produto_e_recusado(loja):
    loja.login("aluno", "selenium123")
    loja.driver.find_element(By.ID, "cliente").send_keys("Sem produto")
    loja.driver.find_element(By.CSS_SELECTOR, "[data-testid=enviar-pedido]").click()

    assert loja.driver.find_element(By.ID, "mensagem-pedido").text == "Preencha cliente e produto."
    assert len(loja.linhas_da_tabela()) == 3


def test_relatorio_conta_os_pedidos(loja):
    loja.login("aluno", "selenium123")
    loja.criar_pedido("Duda", "Doce de leite")
    assert loja.carregar_relatorio() == "Total de pedidos: 4"
