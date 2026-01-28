# Artisan 📱

**Artisan** é uma solução Android completa para gestão empresarial, focada em prestadores de serviços e ateliês. O aplicativo oferece controle total sobre orçamentos, agenda, clientes e fluxo financeiro.

Este projeto foi desenvolvido utilizando as melhores práticas de desenvolvimento Android moderno, incluindo arquitetura MVVM e Kotlin.

## ✨ Funcionalidades

O sistema é dividido em módulos robustos para atender diversas necessidades do negócio:

* **👥 Gestão de Clientes:** Cadastro completo e histórico de interações.
* **📄 Orçamentos Inteligentes:**
    * Criação detalhada de orçamentos (materiais, mão de obra, taxas).
    * **Geração de PDF** automática para envio ao cliente.
    * Cálculo automático de margens e lucros.
* **📅 Agenda Integrada:** Visualização de compromissos e prazos de entrega.
* **💰 Financeiro:**
    * Controle de Recebimentos e Baixas.
    * Gestão de Comissões (para arquitetos e parceiros).
    * Relatórios de desempenho.
* **📦 Estoque e Materiais:** Cadastro de insumos e cálculo de custos.
* **🔐 Segurança:** Sistema de Login e autenticação segura.

## 🛠 Tecnologias Utilizadas

O projeto foi construído com **Kotlin** e segue a arquitetura **MVVM (Model-View-ViewModel)**.

* **Interface (UI):** XML Layouts, Material Design.
* **Injeção de Dependência & Arquitetura:** ViewBinding, ViewModel, LiveData.
* **Banco de Dados Local:** Room Database (SQLite abstraído).
* **Conexão de Rede:** Retrofit 2 + Gson (para comunicação com API).
* **Assincronismo:** Kotlin Coroutines.
* **Utilitários:**
    * Gerador de PDF nativo.
    * Conversão de HTML para Imagem.
    * Manipulação de máscaras monetárias.

## 🚀 Como rodar o projeto

### Pré-requisitos
* Android Studio Ladybug ou superior.
* JDK 17 ou superior.

### Passo a passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/artisan.git](https://github.com/SEU-USUARIO/artisan.git)
    ```
2.  **Abra no Android Studio:**
    * Inicie o Android Studio e selecione "Open an existing project".
    * Navegue até a pasta clonada.
3.  **Sincronize o Gradle:**
    * Aguarde o download das dependências. Se houver erro, vá em *File > Sync Project with Gradle Files*.
4.  **Execute:**
    * Conecte um dispositivo físico ou inicie um Emulador.
    * Clique no botão "Run" (▶).

## 📂 Estrutura do Projeto

```text
mobile-app/
├── app/src/main/java/com/sttalis/artisan/
│   ├── api/          # Configuração do Retrofit e Endpoints
│   ├── data/         # Room DAOs e Repositórios
│   ├── model/        # Data Classes (Entidades)
│   ├── ui/           # Activities, Fragments e Adapters
│   └── utils/        # Geradores de PDF, Formatações, etc.
└── assets/           # Templates HTML para geração de relatórios