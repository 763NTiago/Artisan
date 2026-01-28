# Artisan - Suite de Gestão Empresarial

**Artisan** é um ecossistema completo para gestão de negócios, ateliês e prestadores de serviços. O projeto integra múltiplas plataformas para oferecer controle total sobre orçamentos, agenda, clientes e fluxo financeiro.

Este repositório opera como um **Monorepo**, contendo as três frentes do sistema:

---

## 📂 Estrutura do Projeto

O sistema é dividido em três módulos principais. Clique nos links para ver a documentação específica de cada um:

### 📱 1. [Mobile App (Android)](./mobile-app)
Aplicativo nativo para o dia a dia, focado na agilidade e atendimento ao cliente.
* **Tecnologia:** Kotlin, MVVM, Room Database.
* **Funcionalidades:** Agenda, criação rápida de orçamentos, consulta de clientes.
* [Ver instruções do Mobile](./mobile-app/README.md)

### 💻 2. [Desktop App (Windows)](./desktop-app)
Software robusto para a administração do escritório.
* **Tecnologia:** Python (CustomTkinter), Geração de PDF (wkhtmltopdf).
* **Funcionalidades:** Relatórios complexos, gestão de estoque, configurações do sistema, geração de contratos.
* [Ver instruções do Desktop](./desktop-app/Readme.md)

### ☁️ 3. [Backend API](./backend-api)
Servidor central para sincronização e inteligência de dados.
* **Tecnologia:** Python (Django Rest Framework).
* **Funcionalidades:** Centralização dos dados, API REST, autenticação e backup.
* [Ver instruções do Backend](./backend-api/README.md)

---

## 🛠 Tecnologias Globais

* **Linguagens:** Kotlin, Python.
* **Banco de Dados:** SQLite (Local) / PostgreSQL (Produção).
* **Design:** Material Design (Mobile) / Interface Moderna (Desktop).

