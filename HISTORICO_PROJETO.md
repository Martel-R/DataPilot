# Histórico do Projeto: DataPilot

Este documento registra a jornada de desenvolvimento e as decisões de arquitetura tomadas durante a criação do projeto DataPilot.

## Fase 1: Concepção e Estrutura Inicial

- **Arquiteto de Software:** Atuando como Arquiteto, foi idealizada uma stack de Data & IA Conversacional.
- **Criação do `docker-compose.yml`:** Foi gerado um arquivo Docker Compose para orquestrar os seguintes serviços:
  - **MinIO:** Servidor de armazenamento S3 local.
  - **Airflow:** Orquestrador de pipelines (scheduler e webserver).
  - **Neo4j:** Banco de dados de grafos.
  - **Spark:** Ambiente PySpark com master e worker.
  - **Backend/FastAPI:** API em Python para servir a aplicação.
- **Criação do Projeto:** A estrutura de diretórios `DataPilot` foi criada, incluindo pastas para DAGs (`dags`), logs (`logs`), aplicações Spark (`spark-apps`) e o código do backend (`backend`).

## Fase 2: Separação de Ambientes e Boas Práticas

- **Engenheiro de Segurança:** Atuando como Engenheiro, foi introduzida a separação de ambientes.
- **Refatoração para Múltiplos Ambientes:** A configuração do Docker Compose foi dividida em:
  - `docker-compose.base.yml`: Configurações comuns a todos os ambientes.
  - `docker-compose.dev.yml`: Overrides para desenvolvimento (hot-reloading, portas expostas).
  - `docker-compose.prod.yml`: Overrides para produção (restart policies, Gunicorn).
- **Criação do `.env`:** As credenciais e configurações foram movidas para um arquivo `.env` para evitar segredos no código-fonte.

## Fase 3: Implementação dos Módulos de Dados e IA

- **Engenheiro de Dados Sênior:** Atuando como Engenheiro de Dados, foi criado o principal pipeline de processamento.
- **Criação do Script PySpark:** Foi desenvolvido o script `process_vendas.py` para:
  - Ler dados brutos do MinIO (`bronze`).
  - Aplicar transformações (limpeza, filtros, conversão de tipos).
  - Salvar os dados processados em formato **Delta Lake** na camada `gold`, particionados por mês.
- **Desenvolvedor Full-Stack:** Atuando como Desenvolvedor, foi criado um esqueleto da API de IA.
- **Endpoint de Chat Simulado:** Foi adicionado o endpoint `POST /chat` que simula uma chamada a um LLM (Gemini) e a seleção de uma ferramenta (SQL_TOOL vs. ML_PREDICT_TOOL).
- **Endpoint de Segurança:** Foi criado o endpoint `POST /api/v1/registrar_conexao` para registrar conexões de banco de dados, implementando a criptografia da senha com a biblioteca `cryptography` (Fernet).

## Fase 4: Evolução para Arquitetura Multitenant

- **Arquiteto de Software:** Atuando como Arquiteto, o projeto foi evoluído para suportar múltiplas organizações (assinaturas).
- **Isolamento de Dados:** A estratégia de armazenamento no MinIO foi definida para usar prefixos por organização (ex: `org_id=org_a/...`).
- **Implementação de Autenticação JWT:**
  - Foi criado um módulo `security.py` para gerenciar hashing de senhas e tokens JWT.
  - A API foi refatorada para incluir um endpoint de login (`/api/v1/token`) e proteger o endpoint `/chat`.
  - O endpoint `/chat` agora opera no contexto da organização do usuário logado.
- **Parametrização do Pipeline de Dados:** O script `process_vendas.py` foi modificado para aceitar um `organization_id` como argumento, tornando-o capaz de processar dados para uma organização específica de cada vez.

## Fase 5: Integração com Supabase (Em Andamento)

- **Decisão Arquitetural:** Foi decidido substituir a autenticação customizada e o MinIO local pelos serviços do Supabase para aumentar a robustez e segurança.
- **Setup Local do Supabase:** Foram fornecidas as instruções para o usuário iniciar o ambiente Supabase localmente via Docker, utilizando a CLI oficial do Supabase.
- **Próximo Passo:** Aguardando as credenciais do ambiente Supabase local para prosseguir com a refatoração do código e integração.
