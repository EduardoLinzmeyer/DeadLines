from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

from backend import database, auth

router = APIRouter()



"""Modelos Pydantic para validação dos dados de entrada"""
class UserBase(BaseModel):
    username: str
    nome_completo: str
    nivel_acesso: str
    ativo: bool

class UserCreate(BaseModel):
    username: str
    password: str
    nome_completo: str
    nivel_acesso: str
    ativo: bool = True

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    nivel_acesso: Optional[str] = None
    ativo: Optional[bool] = None
    redefinir_senha: Optional[bool] = None

class User(UserBase):
    id: int
    class Config:
        orm_mode = True


"""Rotas para gerenciar usuários"""
"""Obtém a listagem de todos os usuários existentes"""
@router.get("/", response_model=List[User])
async def read_users():
    users_db = database.obter_usuarios()
    if not users_db:
        return []

    return [
        User(
            id=user['id'],
            username=user['username'],
            nome_completo=user['nome_completo'],
            nivel_acesso=user['nivel_acesso'],
            ativo=user['ativo']
        )
        for user in users_db
    ]


"""Cria um novo usuário"""
@router.post("/", response_model=User)
async def create_user(user_data: UserCreate):
    user_id = database.criar_usuario(
        username=user_data.username,
        password=user_data.password,
        nome_completo=user_data.nome_completo,
        nivel_acesso=user_data.nivel_acesso,
        ativo=user_data.ativo
    )

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já existe ou erro ao criar.")

    created_user_data = database.obter_usuario_por_id(user_id)
    return User(
        id=created_user_data[0],
        username=created_user_data[1],
        nome_completo=created_user_data[3],
        nivel_acesso=created_user_data[5],
        ativo=bool(created_user_data[6])
    )


"""Atualiza um usuário existente"""
@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate):
    existing_user = database.obter_usuario_por_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    success = database.atualizar_usuario(
        user_id=user_id,
        nome_completo=user_data.nome_completo,
        nivel_acesso=user_data.nivel_acesso,
        ativo=user_data.ativo,
        redefinir_senha=user_data.redefinir_senha
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao atualizar usuário.")

    updated_user_data = database.obter_usuario_por_id(user_id)
    return User(
        id=updated_user_data[0],
        username=updated_user_data[1],
        nome_completo=updated_user_data[3],
        nivel_acesso=updated_user_data[5],
        ativo=bool(updated_user_data[6])
    )


"""Deleta um usuário"""
@router.delete("/{user_id}")
async def delete_user(user_id: int):
    success = database.deletar_usuario(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return {"message": "Usuário deletado com sucesso."}
