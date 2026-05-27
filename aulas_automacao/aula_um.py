import pyautogui as pyag
import pandas as pd
import time
import subprocess
import os
import sys
import logging
import platform
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
# 1. CONFIGURAÇÕES GLOBAIS
# ─────────────────────────────────────────────

# Arquivo de log com timestamp único por execução
LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    f"automacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# Segurança: move o mouse para o canto = emergência/abort
pyag.FAILSAFE = True

# Pausa padrão entre ações (pode ser reduzida em máquinas mais rápidas)
pyag.PAUSE = 0.4

# ─────────────────────────────────────────────
# 2. CONSTANTES DE CONFIGURAÇÃO
# ─────────────────────────────────────────────

URL_LOGIN       = "https://dlp.hashtagtreinamentos.com/python/intensivao/login"
EMAIL           = "hellommay@gmail.com"
SENHA           = "senha1234567"
TEMPO_CARREGAMENTO_SITE  = 6    # segundos após abrir o navegador
TEMPO_APOS_LOGIN         = 4    # segundos após clicar em entrar
TEMPO_APOS_CADASTRO      = 0.5  # segundos após cada produto

# Coordenadas dos campos — ajuste conforme a resolução do seu monitor
COORD_EMAIL = (64, 97)   # campo e-mail na tela de login
COORD_CODIGO = (67, 118)   # primeiro campo do formulário de produto

# Colunas obrigatórias no CSV
COLUNAS_OBRIGATORIAS = [
    "codigo", 
    "marca", 
    "tipo", 
    "categoria", 
    "preco_unitario", 
    "custo"
]


# ─────────────────────────────────────────────
# 3. DATACLASS DE RESULTADO
# ─────────────────────────────────────────────

@dataclass
class Resultado:
    total:      int = 0
    sucesso:    int = 0
    falha:      int = 0
    erros:      list = field(default_factory=list)

    def registrar_sucesso(self):
        self.sucesso += 1

    def registrar_falha(self, linha: int, motivo: str):
        self.falha += 1
        self.erros.append({"linha": linha, "motivo": motivo})

    def imprimir_relatorio(self):
        log.info("=" * 50)
        log.info("RELATÓRIO FINAL DE EXECUÇÃO")
        log.info("=" * 50)
        log.info(f"  Total de produtos no CSV : {self.total}")
        log.info(f"  Cadastrados com sucesso  : {self.sucesso}")
        log.info(f"  Falhas                   : {self.falha}")
        if self.erros:
            log.warning("  Detalhes das falhas:")
            for e in self.erros:
                log.warning(f"    Linha {e['linha']}: {e['motivo']}")
        log.info("=" * 50)


# ─────────────────────────────────────────────
# 4. FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def abrir_navegador(url: str) -> None:
    """Abre a URL no navegador padrão de forma multiplataforma."""
    sistema = platform.system()
    log.info(f"Sistema operacional: {sistema}")
    log.info(f"Abrindo navegador em: {url}")

    try:
        if sistema == "Windows":
            os.startfile(url)
        elif sistema == "Darwin":           # macOS
            subprocess.Popen(["open", url])
        else:                               # Linux
            subprocess.Popen(["xdg-open", url])
    except Exception as e:
        log.error(f"Falha ao abrir o navegador: {e}")
        raise

    log.info(f"Aguardando {TEMPO_CARREGAMENTO_SITE}s para o site carregar...")
    time.sleep(TEMPO_CARREGAMENTO_SITE)


def fazer_login(email: str, senha: str) -> None:
    """Preenche o formulário de login e entra no sistema."""
    log.info("Realizando login...")
    try:
        pyag.click(*COORD_EMAIL)
        time.sleep(0.3)
        pyag.write(email, interval=0.05)
        pyag.press("tab")
        pyag.write(senha, interval=0.05)
        pyag.press("tab")
        pyag.press("enter")
        log.info(f"Aguardando {TEMPO_APOS_LOGIN}s após login...")
        time.sleep(TEMPO_APOS_LOGIN)
    except pyag.FailSafeException:
        log.critical("FAILSAFE ativado! Mouse levado ao canto da tela.")
        sys.exit(1)


def carregar_csv(caminho: str) -> pd.DataFrame:
    """Carrega e valida o CSV de produtos."""
    if not os.path.exists(caminho):
        log.error(f"Arquivo não encontrado: {caminho}")
        raise FileNotFoundError(f"CSV não encontrado: {caminho}")

    try:
        tabela = pd.read_csv(caminho, dtype=str)
    except Exception as e:
        log.error(f"Erro ao ler o CSV: {e}")
        raise

    # Remove espaços em branco dos nomes de colunas
    tabela.columns = tabela.columns.str.strip()

    # Verifica colunas obrigatórias
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in tabela.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes no CSV: {faltando}")

    # Remove linhas completamente vazias
    tabela.dropna(how="all", inplace=True)
    tabela.reset_index(drop=True, inplace=True)

    log.info(f"CSV carregado com sucesso: {len(tabela)} produto(s) encontrado(s).")
    log.info(f"Colunas: {list(tabela.columns)}")
    return tabela


def escrever_campo(valor: Optional[str], pular: bool = True) -> None:
    """
    Digita um valor no campo atual e avança com TAB.
    - Trata NaN como campo vazio.
    - Usa intervalo entre teclas para evitar perda de caracteres.
    """
    texto = "" if pd.isna(valor) or str(valor).strip().lower() == "nan" else str(valor).strip()
    if texto:
        pyag.write(texto, interval=0.05)
    if pular:
        pyag.press("tab")


def cadastrar_produto(linha: int, tabela: pd.DataFrame) -> None:
    """Preenche o formulário completo de um produto."""
    pyag.click(*COORD_CODIGO)
    time.sleep(0.2)

    escrever_campo(tabela.loc[linha, "codigo"])
    escrever_campo(tabela.loc[linha, "marca"])
    escrever_campo(tabela.loc[linha, "tipo"])
    escrever_campo(tabela.loc[linha, "categoria"])
    escrever_campo(tabela.loc[linha, "preco_unitario"])
    escrever_campo(tabela.loc[linha, "custo"])

    # OBS é opcional
    obs_col = "obs" if "obs" in tabela.columns else None
    obs = tabela.loc[linha, obs_col] if obs_col else None
    escrever_campo(obs, pular=True)   # TAB mesmo se vazio

    pyag.press("enter")
    time.sleep(TEMPO_APOS_CADASTRO)

    # Scroll para topo para o próximo produto
    pyag.hotkey("ctrl", "home")


# ─────────────────────────────────────────────
# 5. FLUXO PRINCIPAL
# ─────────────────────────────────────────────

def main():
    resultado = Resultado()

    # Caminho do CSV relativo ao script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(diretorio_atual, "produtos.csv")

    log.info("Iniciando automação de cadastro de produtos.")

    # Abre o site
    abrir_navegador(URL_LOGIN)

    # Login
    fazer_login(EMAIL, SENHA)

    # Carrega a planilha
    tabela = carregar_csv(caminho_csv)
    resultado.total = len(tabela)

    # Loop de cadastro
    for linha in tabela.index:
        codigo = str(tabela.loc[linha, "codigo"]).strip()
        log.info(f"[{linha + 1}/{resultado.total}] Cadastrando produto: {codigo}")

        try:
            cadastrar_produto(linha, tabela)
            resultado.registrar_sucesso()
            log.info(f"  ✔ Produto '{codigo}' cadastrado.")

        except pyag.FailSafeException:
            log.critical("FAILSAFE ativado! Encerrando automação.")
            break

        except Exception as e:
            motivo = str(e)
            log.error(f"  ✘ Falha no produto '{codigo}': {motivo}")
            resultado.registrar_falha(linha, motivo)
            # Continua para o próximo produto em vez de travar tudo
            continue

    # Relatório final
    resultado.imprimir_relatorio()
    log.info(f"Log salvo em: {LOG_FILE}")


if __name__ == "__main__":
    main()
