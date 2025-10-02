from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

from backend import database
from backend.api import users
from backend.auth import criar_token_acesso



"""Config. da aplicação FastAPI"""
app = FastAPI(
    title="DeadLines API",
    description="API para gerenciamento de tarefas e agendamentos",
    version="1.0.0"
)


"""Config. CORS p/ permitir frontend"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""Modelos Pydantic"""
class TemaPreferido(BaseModel):
    tema: str

class User(BaseModel):
    id: int
    username: str
    nome_completo: str
    tema_preferido: str
    nivel_acesso_id: int
    nivel_acesso_nome: str

class UserLogin(BaseModel):
    username: str
    password: str

class Task(BaseModel):
    id: Optional[int] = None
    content: str
    due_date: date
    user_id: int
    create_at: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenWithTheme(Token):
    user: User


"""Inclui o router de usuários, definindo o prefixo da rota"""
app.include_router(users.router, prefix="/users", tags=["users"])


"""Rotas da API"""
@app.get("/health")
async def health_check():
    return {"message": "API Backend OK", "status": "healthy"}

@app.get("/")
async def root():
    return {"message": "DeadLines API - Acesse /docs para documentação"}


"""Rota de login"""
@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_db = database.verificar_login(form_data.username, form_data.password)

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gerar o token com o ID e username do usuário
    token_payload = {
        "sub": user_db["id"],       # "sub" usado pra o ID do usuário
        "username": user_db["username"]
    }
    access_token = criar_token_acesso(token_payload)

    # Retorna o token e os dados do usuário
    user = {
        "id": user_db["id"],
        "username": user_db["username"],
        "nome_completo": user_db["nome_completo"],
        "tema_preferido": user_db["tema_preferido"],
        "nivel_acesso_id": user_db["nivel_acesso_id"],
        "nivel_acesso_nome": user_db["nivel_acesso_nome"],
        "ativo": user_db["ativo"]
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


"""Rotas de Tarefas"""
@app.get("/tasks/user/{user_id}", response_model=List[Task])
async def obter_tarefas_de_usuarios(user_id: int):
    tarefas_do_bd = database.obter_tarefas_por_usuario_id(user_id)
    tasks = [
        Task(id=row[0], content=row[1], due_date=row[2], user_id=user_id)
        for row in tarefas_do_bd
    ]
    return tasks

@app.post("/tasks/", response_model=Task)
async def criar_tarefa(task: Task):
    success = database.inserir_tarefa(task.content, task.due_date, task.user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Erro ao criar tarefa")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def alterar_tarefa_api(task_id: int, task: Task):
    success = database.alterar_tarefa(task_id, task.content, task.due_date, task.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada ou erro de alteração")
    return task

@app.delete("/tasks/{task_id}")
async def deletar_tarefa_api(task_id: int, user_id: int):
    success = database.deletar_tarefa(task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"ok": True}

@app.get("/tasks/{task_id}", response_model=Task)
async def obter_tarefa_api(task_id: int, user_id: int):
    tarefa_do_bd = database.obter_tarefa_por_id(task_id, user_id)
    if not tarefa_do_bd:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return Task(id=tarefa_do_bd[0], content=tarefa_do_bd[1], due_date=tarefa_do_bd[2], user_id=user_id)


"""Rotas para gerenciar o tema"""
@app.get("/user/{user_id}/theme", response_model=TemaPreferido)
async def obter_tema_do_usuario(user_id: int):
    tema = database.obter_tema_preferido(user_id)
    return {"tema": tema}

@app.put("/user/{user_id}/theme", response_model=TemaPreferido)
async def alterar_tema_do_usuario(user_id: int, tema_data: TemaPreferido):
    print(f"DEBUG: Recebida solicitação para atualizar tema do usuário {user_id} para '{tema_data.tema}'")
    success = database.atualizar_preferencia_tema(user_id, tema_data.tema)
    if not success:
        print(f"DEBUG: Falha ao atualizar tema para usuário {user_id}")
        raise HTTPException(status_code=400, detail="Erro ao atualizar tema")
    print(f"DEBUG: Tema atualizado com sucesso para usuário {user_id}")
    return {"tema": tema_data.tema}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host="0.0.0.0",
                port=8000)

"""Executar separadamente em ambiente de Desenvolvimento"""
"""
    Para backend: 
    uvicorn backend.main:app --reload na pasta raiz DeadLines
    
    Para frontend: 
    python main.py
"""