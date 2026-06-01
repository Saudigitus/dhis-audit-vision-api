# DHIS2_AUDIT_VISION

Projecto para implementação de visualização de audits do DHIS2.

## Execução com Docker

### 1. Configuração das variáveis de ambiente

Crie o ficheiro `.env` e substitua os valores de exemplo necessários:

```sh
cp .env.example .env
```

### 2. Build e inicialização dos serviços

```sh
docker compose up --build -d
```

A API ficará disponível em `http://localhost:8000` e a documentação
interactiva em `http://localhost:8000/docs`.

### 3. Execução das migrations

```sh
docker compose exec api alembic upgrade head
```

Para criar uma nova migration:

```sh
docker compose exec api alembic revision --autogenerate -m "Descrição da migration"
```

### 4. Criação do super-utilizador

```sh
docker compose exec api python commands.py seed-superuser
```

### 5. Logs e encerramento

```sh
docker compose logs -f api
docker compose down
```

Os dados do PostgreSQL, os ficheiros de auditoria e os logs são persistidos
em volumes Docker.

## Execução local

### 1. Criação do ambiente virtual
```sh
python -m venv .venv
```

### 2. Activação do ambiente virtual

No Windows:

```sh
. .venv/Scripts/activate
```

### 3. Instalação dependências
```sh
pip install -r requirements.txt
```

### 4. Actualização das variáveis de ambiente

Crie o ficheiro `.env` na raiz do projecto a partir de `.env.example`.

### 5. Executar migração da base de dados

#### 5.1. Criação das migrations
```sh
alembic revision --autogenerate -m "Descrição da migration"
```

#### 5.2. Aplicar as migrations
```sh
alembic upgrade head
```

#### 5.3. Criar o super-utilizador
```sh
python commands.py seed-superuser
```

### 6. Inicialização do servidor
```sh
python runserver.py
```
