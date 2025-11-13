# 🐍 Django + PostgreSQL com Docker

Este projeto utiliza **Django (Python)** para o backend e **PostgreSQL** como banco de dados, gerenciado via **Docker Compose**.  
O guia abaixo descreve os passos para rodar a aplicação em outra máquina.

---

## 🚀 Pré-requisitos

Antes de começar, instale os seguintes programas:

1. **Git** – [https://git-scm.com/downloads](https://git-scm.com/downloads)
2. **Docker e Docker Compose** – [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
3. **Python 3.10+** – [https://www.python.org/downloads/](https://www.python.org/downloads/)

---

## 🧭 Passo a Passo para Executar o Projeto

### 1️⃣ Clonar o repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_DIRETORIO_DO_PROJETO>

2️⃣ Subir o banco de dados com Docker

No diretório do projeto, execute:

docker-compose up -d


Isso irá baixar e iniciar o container do PostgreSQL em segundo plano.

3️⃣ Criar e ativar um ambiente virtual
python -m venv .venv


Ative o ambiente:

Windows

.venv\Scripts\activate


Linux/macOS

source .venv/bin/activate

4️⃣ Instalar as dependências do projeto
pip install -r requirements.txt

5️⃣ Configurar variáveis de ambiente

Crie um arquivo .env na raiz do projeto e adicione suas credenciais, por exemplo:

GEMINI_API_KEY='SUA_CHAVE_API_AQUI'


(O nome e conteúdo podem variar conforme o projeto.)

6️⃣ Aplicar as migrações do banco de dados
python manage.py migrate

7️⃣ Criar um superusuário para o Django Admin
python manage.py createsuperuser


Siga as instruções no terminal para definir usuário e senha.

8️⃣ Rodar o servidor de desenvolvimento
python manage.py runserver


A aplicação estará acessível em:

👉 http://127.0.0.1:8000

🧩 Estrutura básica do projeto
├── manage.py
├── docker-compose.yml
├── requirements.txt
├── .env (não versionado)
├── .gitignore
├── app/ ou src/ (código da aplicação Django)
└── ...

🧰 Comandos úteis

Parar containers Docker:

docker-compose down


Ver logs do banco:

docker-compose logs -f db


Recriar containers (se mudar algo no compose):

docker-compose up -d --build

🛠️ Tecnologias Utilizadas

Python 3.10+

Django

PostgreSQL (via Docker)

Docker Compose

📜 Licença

Este projeto é distribuído sob a licença MIT — sinta-se à vontade para usar e modificar.

✦ Autor: Seu Nome Aqui
✦ Contato: seu.email@exemplo.com


---

Quer que eu adicione também um exemplo de `.env` comentado (com variáveis típicas de Django e banco PostgreSQL)? Isso deixa o setu
