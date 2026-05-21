# Tecnologias e Ambiente
* **Python 3**
* **Linux (Ubuntu)**
* **VsCode / Terminal**
* **Git & GitHub**

## Projetos e Conteúdo

### 1. Automação de Cadastro de Produtos
Script desenvolvido para otimizar o processo de leitura de dados e preenchimento de formulários em plataformas web.
Ele automatiza as etapas de login, processamento de arquivos e inserção de dados, reduzindo o trabalho manual.

* **Destaques Técnicos:**
  * **Manipulação de Dados:** Uso do **Pandas** para ler, estruturar e percorrer bases de dados a partir de arquivos CSV.
  * **Interação com a Interface (GUI):** Uso do **PyAutoGUI** para simular ações humanas de clique, posicionamento de cursor e digitação sequencial.

#### Pré-requisitos e Instalação (Ambiente Linux)
Como o projeto interage com a interface gráfica no Linux, é necessário instalar as dependências do sistema antes das bibliotecas do Python.

```bash
# 1. Atualizar o sistema e instalar dependências de GUI para o PyAutoGUI
sudo apt-get update && sudo apt-get install -y scrot python3-tk python3-dev

# 2. Instalar as bibliotecas do projeto a partir do arquivo abaixo
pip install -r requirements.txt