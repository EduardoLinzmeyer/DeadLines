from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
from dotenv import load_dotenv

from backend import database


load_dotenv()

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET", "minha_chave_supersecreta")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

# Rota padrão onde o cliente pega token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


"""Criar JWT de acesso"""
def criar_token_acesso(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


"""Obtém os dados do usuário a partir do token JWT"""
def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Opcional: buscar usuário no banco
        user = database.obter_usuario_por_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        user_data = {
            "id": user.get("id") if isinstance(user, dict) else user[0],
            "username": user.get("username") if isinstance(user, dict) else user[1],
            "nome_completo": user.get("nome_completo") if isinstance(user, dict) else user[3],
            "nivel_acesso": user.get("nivel_acesso") if isinstance(user, dict) else user[5],
            "ativo": bool(user.get("ativo")) if isinstance(user, dict) else bool(user[6])
        }
        return user_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
