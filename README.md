# DHIS2_AUDIT_VISION

Projecto para implementação de visualização de audits do dhis2

### 1. Criação ambiente virtual
```sh
   python -m venv .venv
```

### 2. Activação do ambiente virtual
O comando de activação para o sistema operativo Windows
```sh
   . .venv/Scripts/activate
```

### 3. Instalação dependências
```sh
   pip install -r requirements.txt
```

### 4. Actualização das variáveis de ambiente
Crie o ficheiro .env no root da pasta do projecto e preencha as seguintes variáveis:

```sh
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
```
### 5. Executar migração da base de dados

#### 5.1. Criação das migrations
```sh
alembic revision --autogenerate -m "Create all tables (Essa é só uma mensagem descritiva da migration)"
```
#### 5.2 Aplicar as migrations
```sh
alembic upgrade head
```

#### 5.3 Executar seeders
```sh
python commands.py
```

### 6. Inicialização do servidor
```sh
  python runserver.py
```
