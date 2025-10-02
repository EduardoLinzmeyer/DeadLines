import httpx
from typing import Optional, Dict, Any, List
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token: Optional[str] = None
        logger.debug(f"API Client inicializado com base_url: {self.base_url}")


    """Testa conexão com a API"""
    async def conexao_teste(self) -> Optional[Dict[str, Any]]:
        try:
            logger.debug(f"Testando conexão com: {self.base_url}/health")
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=10.0
            )
            logger.debug(f"Resposta API: Status {response.status_code}, Body {response.text}")

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API retornou status {response.status_code}")
                return None

        except httpx.ConnectError:
            logger.warning(f"Não foi possível conectar com {self.base_url}")
            return None
        except httpx.TimeoutException:
            logger.error("Timeout ao conectar com a API")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao testar conexão: {e}")
            return None


    """Retorna headers de autenticação"""
    def obter_cabecalho_de_autenticacao(self) -> Dict[str, str]:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}


    """Autentica usuário na API"""
    async def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            login_data = {
                "username": username,
                "password": password
            }

            response = await self.client.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                timeout=30.0
            )

            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return data
            return None

        except Exception as e:
            print(f"Erro no login: {e}")
            return None


    async def obter_tema_do_usuario(self, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.get(
                f"{self.base_url}/user/{user_id}/theme",
                    headers=headers
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Erro ao obter tema do usuário: {e}")
            return {"tema": "claro"}


    async def alterar_tema_do_usuario(self, user_id: int, tema: str):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            payload = {"tema": tema}
            response = await self.client.put(
                f"{self.base_url}/user/{user_id}/theme",
                json=payload,
                headers=headers
            )
            return response.status_code in (200, 201, 204)

        except Exception as e:
            print(f"Erro na PAI ao alterar o tema do usuário: {e}")
            return False


    async def obter_tarefas_de_usuarios(self, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.get(f"{self.base_url}/tasks/user/{user_id}", headers=headers)
            return response.json()

        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")
            return None


    async def criar_tarefa(self, content: str, due_date: str, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.post(
                f"{self.base_url}/tasks/",
                json={"content": content, "due_date": due_date, "user_id": user_id},
                headers=headers
            )
            return response.status_code in (200, 201, 204)

        except Exception as e:
            print(f"Erro ao criar tarefa: {e}")
            return False


    async def alterar_tarefa(self, task_id: int, content: str, due_date: str, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.put(
                f"{self.base_url}/tasks/{task_id}",
                json={"content": content, "due_date": due_date, "user_id": user_id},
                headers=headers
            )
            return response.status_code == 200

        except Exception as e:
            print(f"Erro ao atualizar tarefa: {e}")
            return False


    async def deletar_tarefa(self, task_id: int, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.delete(
                f"{self.base_url}/tasks/{task_id}",
                params={"user_id": user_id},
                headers=headers
            )
            return response.status_code == 200

        except Exception as e:
            print(f"Erro ao excluir tarefa: {e}")
            return False


    async def obter_tarefa(self, task_id: int, user_id: int):
        try:
            headers = self.obter_cabecalho_de_autenticacao()
            response = await self.client.get(
                f"{self.base_url}/tasks/{task_id}",
                params={"user_id": user_id},
                headers=headers
            )
            return response.json()

        except Exception as e:
            print(f"Erro ao buscar tarefa: {e}")
            return None


    """Obtém a lista de todos os usuários"""
    async def get_users(self):
        try:
            response = await self.client.get(f"{self.base_url}/users/")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao obter usuários: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Erro ao obter usuários: {e}")
            return None


    """Cria um novo usuário"""
    async def criar_usuario(self, user_data: Dict[str, Any]) -> bool:
        try:
            response = await self.client.post(
                f"{self.base_url}/users/",
                json=user_data
            )
            response.raise_for_status()
            return response.status_code in (200, 201)

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao criar usuário: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False


    """Atualiza um usuário existente"""
    async def alterar_usuario(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        try:
            response = await self.client.put(
                f"{self.base_url}/users/{user_id}",
                json=user_data
            )
            response.raise_for_status()
            return response.status_code in (200, 201, 204)

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao atualizar usuário: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            return False


    """Deleta usuário"""
    async def deletar_usuario(self, user_id: int) -> bool:
        try:
            response = await self.client.delete(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
            return response.status_code in (200, 201, 204)

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao deletar usuário: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"Erro ao deletar usuário: {e}")
            return False


    async def fechar(self):
        await self.client.aclose()


"""Local para desenvolvimento"""
api_client = APIClient()
