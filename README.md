# DataPilot

> Plataforma de backend para análise de dados conversacional com stack de Data & AI (FastAPI, Airflow, Spark, Delta Lake). Arquitetura multitenant orquestrada via Docker que garante o isolamento e segurança dos dados de cada organização.

---

##  архитектура

O DataPilot utiliza uma arquitetura de microsserviços orquestrada com Docker Compose, projetada para ser escalável e segura. As principais camadas são:

1.  **Camada de Acesso e Interação (FastAPI):** Uma API Python que serve como ponto de entrada. Ela é responsável pela autenticação de usuários (via JWT), autorização e por servir os endpoints da aplicação, como o `/chat`.

2.  **Camada de Orquestração (Airflow):** Responsável por agendar e automatizar os pipelines de dados (DAGs). O Airflow coordena a extração de dados brutos e dispara os jobs de processamento.

3.  **Camada de Processamento (Spark):** Um cluster Spark é utilizado para o processamento em larga escala (ETL). Os scripts PySpark são parametrizados para processar dados de organizações específicas de forma isolada.

4.  **Camada de Armazenamento (MinIO & Delta Lake):** Um Data Lake implementado com MinIO armazena os dados em diferentes estágios (bronze, gold). O formato **Delta Lake** é utilizado na camada `gold` para garantir transações ACID, versionamento e performance.

5.  **Bancos de Dados Adicionais:**
    *   **PostgreSQL:** Serve como o backend de metadados para o Airflow.
    *   **Neo4j:** Disponível para modelagem de dados em grafo.

## Tecnologias Utilizadas

- **Backend:** FastAPI, Gunicorn, Uvicorn
- **Processamento de Dados:** Apache Spark, Delta Lake
- **Orquestração:** Apache Airflow
- **Armazenamento:** MinIO (S3-compatible)
- **Bancos de Dados:** PostgreSQL, Neo4j
- **Autenticação:** JWT (python-jose, passlib)
- **Containerização:** Docker, Docker Compose

## Como Executar o Projeto

### 1. Pré-requisitos

- Docker
- Docker Compose

### 2. Configuração

Antes de iniciar, configure suas variáveis de ambiente.

```sh
# Copie o arquivo de exemplo para criar seu arquivo de ambiente local
cp .env.example .env
```

Abra o arquivo `.env` e revise as configurações. Para desenvolvimento local, os valores padrão devem funcionar.

### 3. Iniciando o Ambiente de Desenvolvimento

Este comando irá construir as imagens e iniciar todos os serviços com hot-reloading para o backend.

```sh
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up --build
```

### 4. Iniciando o Ambiente de Produção

Este comando inicia os serviços em modo "detached" com políticas de reinicialização e sem hot-reloading.

```sh
docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d --build
```

## Acesso aos Serviços

- **API (FastAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Airflow UI:** [http://localhost:8080](http://localhost:8080) (usuário: `admin`, senha: `admin`)
- **Spark Master UI:** [http://localhost:8081](http://localhost:8081)
- **MinIO Console:** [http://localhost:9001](http://localhost:9001) (usuário: `minioadmin`, senha: `minioadmin`)
- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474) (usuário: `neo4j`, senha: `password`)

## Estrutura do Projeto

```
DataPilot/
├── backend/         # Código-fonte da API FastAPI e segurança
├── dags/            # Diretório para os DAGs do Airflow
├── spark-apps/      # Scripts PySpark para processamento de dados
├── .env             # (Não versionado) Suas variáveis de ambiente
├── .env.example     # Template para as variáveis de ambiente
├── docker-compose.* # Arquivos de orquestração do Docker
└── README.md        # Este arquivo
```
