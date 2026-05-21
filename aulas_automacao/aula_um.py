import pyautogui as pyag
import pandas as pd
import time
import subprocess # Biblioteca nativa para executar comandos do sistema
import os

# 1. Configurações Iniciais
pyag.PAUSE = 0.5 
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_csv = os.path.join(diretorio_atual, "produtos.csv")
link = "https://dlp.hashtagtreinamentos.com/python/intensivao/login"

# 2. Como abrir o navegador
print("Abrindo navegador...")
subprocess.Popen(['xdg-open', link])

time.sleep(5)

# 3. Fazer login 
# ATENÇÃO: Pegar as coordenadas exatas no monitor.
pyag.click(x=64, y=97)
pyag.write("hellommay@gmail.com")
pyag.press("tab") 
pyag.write("senha1234567")
pyag.press("tab")
pyag.press("enter")

time.sleep(4) 

# 4. Abrir a base de dados 
tabela = pd.read_csv("produtos.csv")
print(tabela) 

# 5. Cadastrar produtos
for linha in tabela.index: 
    # Clicar no primeiro campo (código do produto)
    pyag.click(x=67, y=118)
    
    # codigo  
    codigo = str(tabela.loc[linha, "codigo"])
    pyag.write(codigo) 
    pyag.press("tab")
    
    # marca
    marca = str(tabela.loc[linha, "marca"])
    pyag.write(marca) 
    pyag.press("tab")
    
    # tipo
    tipo = str(tabela.loc[linha, "tipo"])
    pyag.write(tipo)
    pyag.press("tab")
    
    # categoria
    categoria = str(tabela.loc[linha, "categoria"])
    pyag.write(categoria)
    pyag.press("tab")
    
    # preco
    preco_unitario = str(tabela.loc[linha, "preco_unitario"])
    pyag.write(preco_unitario) 
    pyag.press("tab")
    
    # custo
    custo = str(tabela.loc[linha, "custo"])
    pyag.write(custo)
    pyag.press("tab")
    
    # OBS
    obs = str(tabela.loc[linha, "obs"])
    if obs != "nan":
        pyag.write(obs) 
        
    pyag.press("tab")     
    pyag.press("enter")
  
    pyag.scroll(5000) # looping, volta a tela para cima para o próximo produto
