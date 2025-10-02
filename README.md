# 💻 DeadLines: Aplicação WEB de Gestão de Agendamentos e Fluxo de Receita

---

## 💡 Sobre o Projeto

O DeadLines é uma **aplicação web Full Stack** desenvolvida para auxiliar no **gerenciamento de agendamentos e no controle de fluxo de receita** (entradas e saídas). O objetivo é fornecer uma ferramenta visual e robusta para que pequenos negócios ou profissionais autônomos possam acompanhar a saúde financeira de suas operações.

O projeto está atualmente na fase de **Prova de Conceito (PoC)**, com a arquitetura principal e o sistema de autenticação de usuários totalmente implementados.

---

## 🛠️ Tecnologias Utilizadas

Esta aplicação foi construída utilizando uma stack moderna e eficiente baseada em Python, aproveitando minha experiência em banco de dados e migrando para o desenvolvimento Full Stack.

| Categoria | Tecnologia | Uso |
| :--- | :--- | :--- |
| **Linguagem Principal** | **Python 3.12+** | Base para o Backend e Frontend. |
| **Backend (API)** | **FastAPI** | Criação de APIs rápidas, robustas e com documentação automática para a manipulação dos dados. |
| **Frontend (UI)** | **Flet** | Desenvolvimento da interface de usuário (UI) e garantia de design responsivo. |
| **Banco de Dados** | **SQL Server** | Gerenciamento e armazenamento estruturado dos dados da aplicação. |
| **Cloud/Infra** | **Azure** | Hospedagem e gerenciamento do serviço de Banco de Dados SQL Server. |
| **Controle de Versão** | **Git & GitHub** | Gerenciamento colaborativo e histórico de versões do código. |

---

## ✨ Funcionalidades Implementadas (PoC)

As seguintes funcionalidades já foram estruturadas e implementadas:

* **Sistema de Autenticação:** Rotas API e modelos de dados para **registro e login de usuários** integrados diretamente ao **SQL Server**.
* **Estrutura Full Stack:** Divisão clara entre o serviço de **Backend (FastAPI)** para manipulação de dados e o **Frontend (Flet)** para renderização da interface.
* **Conexão com Banco de Dados:** Configuração de *queries* e modelos de dados básicos para a comunicação com o SQL Server hospedado no Azure.
* **Layout Responsivo:** Estrutura inicial do *layout* focada em responsividade, garantindo a usabilidade em diferentes telas.

### Próximos Passos (Roadmap)

1.  Implementação das funcionalidades CRUD (Create, Read, Update, Delete) para Agendamentos e Listagens.
2.  Desenvolvimento da visualização de gráficos (dashboards) para análise de entradas e saídas de receita.
3.  Implementação de testes unitários para as rotas API.

---

## ⚙️ Como Executar o Projeto Localmente

Siga os passos abaixo para ter uma cópia do projeto em execução na sua máquina local:

### Pré-requisitos

* Python 3.12+
* Pip
* Acesso a uma instância do **SQL Server** (local ou Azure)

### Configuração

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SeuUsuario/SeuRepositorio.git](https://github.com/SeuUsuario/SeuRepositorio.git)
    cd SeuRepositorio
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    .\venv\Scripts\activate   # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuração do Banco de Dados:**
    * Crie um arquivo `.env` na raiz do projeto.
    * Defina sua string de conexão com o SQL Server.
        ```
        # -----------------------------------------
        # Configuração do Banco de Dados SQL Server
        # -----------------------------------------
        DB_SERVER=seu-server-sql.database.windows.net
        DB_NAME=SeuBDSQL
        DB_USER=seu_user
        DB_PASSWORD="sua_senha"
        DB_DRIVER=ODBC Driver 18 for SQL Server
        DB_TIMEOUT=30
        ```
        *(Ajuste o driver conforme sua instalação.)*

5.  **Execução:**
    * Inicie o servidor **FastAPI (Backend)**:
        ```bash
         # Na raiz do projeto rode > uvicorn backend.main:app --reload
        ```
    * Em um novo terminal, inicie o **Flet (Frontend)**:
        ```bash
        # No arquivo frontend do projeto rode > python main.py
        ```
    O aplicativo estará acessível no navegador, dependendo da configuração do Flet.

---

## 🤝 Contribuições

Este projeto está em desenvolvimento individual, mas contribuições são bem-vindas! Se tiver sugestões ou encontrar *bugs*, por favor, abra uma *Issue* ou envie um *Pull Request*.

---

## 📧 Contato

* **Seu Nome:** Eduardo Linzmeyer
* **LinkedIn:** www.linkedin.com/in/eduardo-linzmeyer-6530b3212
* **Email:** linzmeyereduardo@gmail.com

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.
