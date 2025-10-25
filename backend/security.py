# -*- coding: utf-8 -*-
"""
 Módulo de Segurança para o DataPilot

 Contém toda a lógica para:
 - Hashing e verificação de senhas.
 - Criação e decodificação de JSON Web Tokens (JWT).
 - Gerenciamento de dependências de autenticação para endpoints FastAPI.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ==============================================================================
# CONFIGURAÇÃO DE SEGURANÇA
# ==============================================================================

# Contexto para hashing de senhas usando o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticação OAuth2, aponta para o endpoint que gera o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# ATENÇÃO: Chave secreta para assinar os tokens JWT.
# Em produção, DEVE ser carregada de um Secret Manager ou variável de ambiente.
# Use `openssl rand -hex 32` para gerar uma chave forte.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==============================================================================
# MODELOS (PYDANTIC)
# ==============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    organization_id: Optional[str] = None

class User(BaseModel):
    username: str
    organization_id: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# ==============================================================================
# FUNÇÕES DE UTILIDADE
# ==============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde à senha com hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==============================================================================
# LÓGICA DE AUTENTICAÇÃO (DEPENDÊNCIAS FASTAPI)
# ==============================================================================

# --- BANCO DE DADOS DE USUÁRIOS FAKE (PARA DEMONSTRAÇÃO) ---
# Em um sistema real, isso viria de um banco de dados.
FAKE_USERS_DB = {
    "johndoe": {
        "username": "johndoe",
        "organization_id": "org_a",
        "hashed_password": get_password_hash("secret1"),
        "disabled": False,
    },
    "janesmith": {
        "username": "janesmith",
        "organization_id": "org_b",
        "hashed_password": get_password_hash("secret2"),
        "disabled": False,
    }
}

def get_user(db, username: str) -> Optional[UserInDB]:
    """Busca um usuário no banco de dados fake."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

async def get_current_active_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependência para endpoints protegidos.
    Decodifica o token, valida o usuário e retorna os dados do usuário ativo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        organization_id: str = payload.get("org_id")
        if username is None or organization_id is None:
            raise credentials_exception
        token_data = TokenData(username=username, organization_id=organization_id)
    except JWTError:
        raise credentials_exception
    
    user = get_user(FAKE_USERS_DB, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
