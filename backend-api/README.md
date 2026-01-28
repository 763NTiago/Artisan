# Artisan API - Sistema de Gestão para Marcenaria

## 📋 Sobre o Projeto
Este projeto é a API Restful central do ecossistema **Artisan**, uma solução completa desenvolvida para modernizar a gestão de uma marcenaria. O sistema foi projetado para resolver problemas reais, como controle de orçamentos, cronograma de obras (Agenda), gestão financeira e cálculo automatizado de comissões para arquitetos parceiros.

A API serve como backend unificado para dois clientes:
1.  **Desktop App:** Para uso administrativo no escritório.
2.  **Mobile App:** Para consulta rápida e gestão em campo.

## 🚀 Tecnologias e Decisões Técnicas
Para garantir escalabilidade, segurança e facilidade de manutenção, utilizei as seguintes tecnologias:

* **Linguagem:** Python 3.11 (Foco em legibilidade e produtividade).
* **Framework Web:** Django & Django Rest Framework (DRF) - Escolhidos pela robustez na criação de APIs seguras e padronizadas.
* **Banco de Dados:** PostgreSQL (Produção) / SQLite (Dev) - Configuração flexível via variáveis de ambiente.
* **Containerização:** Docker & Docker Compose - Garante que o ambiente de desenvolvimento seja idêntico ao de produção e facilita o *deploy*.
* **Servidor de Aplicação:** Gunicorn & WhiteNoise - Otimização para servir a API e arquivos estáticos em produção.

### Destaques da Implementação
* **Clean Code:** O código foi estruturado seguindo as diretrizes da PEP-8, com ênfase em nomes descritivos e funções com responsabilidade única.
* **Documentação Automática:** Uso de *Docstrings* em classes e métodos para facilitar o entendimento da regra de negócio por outros desenvolvedores.
* **Segurança:** Separação de configurações sensíveis (`SECRET_KEY`, `DB_PASSWORD`) via variáveis de ambiente e configuração de CORS restritiva.

## 🛠️ Como Rodar o Projeto

### Pré-requisitos
* Docker e Docker Compose instalados.

### Passo a Passo
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/artisan-api.git](https://github.com/seu-usuario/artisan-api.git)
    cd artisan-api
    ```

2.  **Suba os containers (API + Banco de Dados):**
    ```bash
    docker-compose up --build
    ```
    *O Docker irá baixar as imagens, instalar as dependências do `requirements.txt` e iniciar o servidor na porta 8000.*

3.  **Acesse a API:**
    O sistema estará rodando em: `http://localhost:8000/api/`

## 📚 Estrutura da API (Endpoints Principais)

A API segue os padrões REST. Abaixo, os principais recursos disponíveis:

| Recurso | Descrição |
| :--- | :--- |
| `/api/clientes/` | Gestão da base de clientes. |
| `/api/orcamentos/` | Criação e histórico de orçamentos (com itens em JSON). |
| `/api/agenda/` | Controle de cronograma (Data de Início e Previsão de Entrega). |
| `/api/financeiro/` | Dashboards com totais a receber, recebidos e projeções. |
| `/api/comissoes/` | Cálculo automático de comissões para parceiros. |

## 📊 Regras de Negócio Importantes
* **Cálculo de Comissões:** Ao registrar um recebimento vinculado a um arquiteto, o sistema calcula automaticamente o valor da comissão baseada na porcentagem configurada, garantindo precisão financeira.
* **Integração de Agenda:** O orçamentos aprovados podem ser convertidos diretamente em cronogramas de obra.

---
*Desenvolvido com foco em resolver problemas reais através de tecnologia limpa e eficiente.*