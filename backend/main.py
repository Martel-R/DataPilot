# -*- coding: utf-8 -*-
"""
API Principal do Projeto DataPilot
"""

import os
from datetime import timedelta

# --- Imports do FastAPI ---
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

# --- Imports de Criptografia e Segurança ---
from cryptography.fernet import Fernet
from security import (
    User,
    Token,
    get_current_active_user,
    create_access_token,
    verify_password,
    get_user,
    FAKE_USERS_DB,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# ==============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================================================

app = FastAPI(
    title="DataPilot API",
    description="API para o projeto de Data & IA Conversacional com suporte a multitenancy.",
    version="0.2.0",
)

# ==============================================================================
# CONFIGURAÇÃO DE CRIPTOGRAFIA (DEMONSTRAÇÃO)
# ==============================================================================
# ATENÇÃO: Esta chave é apenas para demonstração.
KEY_FERNET_DEMO = b'T2l6eUN1M1JkM05oZkI4eU5tNHZyZ0ctdFZfS3dLeURsZz0='
cipher_suite = Fernet(KEY_FERNET_DEMO)

# ==============================================================================
# MODELOS (PYDANTIC)
# ==============================================================================

class ChatRequest(BaseModel):
    pergunta: str

class ConnectionRequest(BaseModel):
    db_type: str
    host: str
    username: str
    password: str

# ==============================================================================
# ENDPOINTS PÚBLICOS
# ==============================================================================

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API do DataPilot!"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}

# ==============================================================================
# ENDPOINTS DE AUTENTICAÇÃO E SEGURANÇA
# ==============================================================================

@app.post("/api/v1/token", response_model=Token, tags=["Autenticação"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login. Recebe usuário e senha, retorna um Access Token JWT.
    """
    user = get_user(FAKE_USERS_DB, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "org_id": user.organization_id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/registrar_conexao", tags=['Segurança'])
async def registrar_conexao(request: ConnectionRequest):
    """
    Registra uma nova conexão de banco de dados, criptografando a senha.
    """
    password_bytes = request.password.encode('utf-8')
    encrypted_password_bytes = cipher_suite.encrypt(password_bytes)
    encrypted_password_str = encrypted_password_bytes.decode('utf-8')
    return {
        "message": f"Conexão para o host '{request.host}' registrada com sucesso.",
        "encrypted_password": encrypted_password_str
    }

# ==============================================================================
# ENDPOINTS PROTEGIDOS (REQUEREM AUTENTICAÇÃO)
# ==============================================================================

@app.post("/api/v1/chat", tags=["IA"])
async def chat_endpoint(request: ChatRequest, current_user: User = Depends(get_current_active_user)):
    """
    Endpoint de chat protegido. Só pode ser acessado com um token JWT válido.
    A lógica é executada no contexto da organização do usuário logado.
    """
    pergunta = request.pergunta
    organization_id = current_user.organization_id

    # Simulação da chamada ao LLM, que agora estaria ciente da organização
    # chamar o modelo Gemini para processar a pergunta no contexto da org '{organization_id}'
    
    # Simulação da decisão da ferramenta
    # LLM decide se usa a SQL_TOOL ou a ML_PREDICT_TOOL
    
    if "vendas" in pergunta.lower() or "sql" in pergunta.lower():
        tool_used = "SQL_TOOL"
        response_data = {
            "organization_id": organization_id,
            "tool_used": tool_used,
            "query": f"SELECT SUM(valor_venda) FROM vendas_limpas WHERE org_id='{organization_id}' AND mes = 10;",
            "simulated_result": f"A soma de vendas para o mês 10 (Organização: {organization_id}) foi de R$ 12.345,00."
        }
    else:
        tool_used = "Nenhuma"
        response_data = {
            "organization_id": organization_id,
            "tool_used": tool_used,
            "simulated_result": "Não entendi a sua pergunta sobre vendas ou previsões."
        }
        
    return response_data