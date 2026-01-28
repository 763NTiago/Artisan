# 🖥️ Sistema de Orçamentos - Desktop Client

> Uma solução **STTaLIs Tech Solutions**.

Este repositório contém o **Módulo Administrativo (Desktop)** do Ecossistema de Gestão de Orçamentos. Projetado para o ambiente de escritório, este software oferece o controle total das regras de negócio, cadastros complexos e o motor de geração de documentos.

Ele atua como o painel de controle central, alimentando a API e complementando a agilidade do aplicativo Mobile.

---

## 📋 Funcionalidades Principais

* **Gestão Centralizada:** CRUD completo de Clientes, Materiais, Fornecedores e Tabelas de Preços.
* **Motor de Documentos:** Geração de Orçamentos em PDF com layout profissional (HTML/CSS renderizado via `wkhtmltopdf`).
* **Dashboard Financeiro:** Visualização de métricas, recebimentos e projeções.
* **Sincronização:** Comunicação RESTful com a API central.
* **Customização:** Configuração de identidade visual (Logos, Rodapés) dinâmica.

## 🛠️ Tecnologias e Ferramentas

* **Linguagem:** Python 3.11+
* **Interface:** CustomTkinter (UI Moderna e Responsiva)
* **Relatórios:** wkhtmltopdf (Engine de renderização PDF)
* **Build & Distribuição:**
    * **PyInstaller:** Compilação do código Python.
    * **Inno Setup:** Criação do instalador profissional para Windows.

---

## 🚀 Configuração Rápida

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure:** Renomeie `config.exemplo.json` para `config.json` e ajuste os dados da API.

---

## 📦 Processo de Build e Distribuição

O processo de criação do software final para o cliente envolve duas etapas: a compilação do executável e a criação do instalador.

### Passo 1: Gerar o Executável (PyInstaller)

Primeiro, transformamos o código Python numa aplicação Windows standalone. Execute o comando abaixo na raiz do projeto:

```bash
pyinstaller --noconsole --name="OrcamentosApp" --icon="icone.ico" --add-data "assets;assets" --add-data "vendor;vendor" --add-data "config.json;." run.py
```

**Resultado:** Será criada uma pasta `dist/OrcamentosApp` contendo o programa compilado.

### Passo 2: Criar o Instalador (Inno Setup)

Para criar o arquivo `setup.exe` que instala o programa no computador do cliente:

1. Baixe e instale o [Inno Setup Compiler](https://jrsoftware.org/isdl.php).
2. Abra o arquivo `setup.iss` (incluso neste repositório) com o Inno Setup.
3. Verifique se os caminhos no script apontam corretamente para a pasta `dist/OrcamentosApp` gerada no Passo 1.
4. Clique no botão **Compile** (Run).

**Resultado:** Será gerado o instalador `Artisan.exe` pronto para distribuição.