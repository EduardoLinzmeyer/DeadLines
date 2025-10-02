import flet as ft
import asyncio
import sys
import pathlib

current_dir = pathlib.Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.append(str(utils_path))

from utils.api_client import APIClient, api_client



class TelaLogin(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.bgcolor = ft.Colors.SURFACE
        self.alignment = ft.alignment.center
        self.padding = 20

        self.campo_username = ft.TextField(
            label="Usuário",
            prefix_icon=ft.Icons.PERSON,
            autofocus=True,
            on_submit=self.em_login,    # P/ acionar o login ao pressionar ENTER
            width=300
        )

        self.campo_password = ft.TextField(
            label="Senha",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_submit=self.em_login,    # P/ acionar o login ao pressionar ENTER
            width=300
        )

        self.botao_login = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGIN, size=26),
                    ft.Text("Entrar", size=18, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            on_click=self.em_login,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=140,
            height=45,
            tooltip="Clique aqui ou pressione ENTER para fazer login"
        )

        self.texto_erro = ft.Text(
            color=ft.Colors.RED,
            visible=False
        )

        self.status_db = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_500,
            italic=True
        )

        """Layout da tela de login"""
        self.content = ft.Column(
            [
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=100, color=ft.Colors.BLUE_700),
                ft.Text("DeadLines", size=40, weight=ft.FontWeight.BOLD),
                ft.Text("Faça a sua organização", size=22, color=ft.Colors.GREY_600),
                ft.Divider(height=40),
                self.campo_username,
                self.campo_password,
                ft.Container(height=20),
                self.botao_login,
                self.texto_erro,
                self.status_db
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )


    """Chamado quando o componente é montado"""
    def did_mount(self):
        try:
            status_db = self.page.session.get("db_conectado")
            api_status = self.page.session.get("api_conectada")

            if api_status == "false":
                self.status_db.value = "Modo offline - API não conectada"
                self.status_db.color = ft.Colors.ORANGE
            else:
                self.status_db.value = "Conectado com o banco de dados"
                self.status_db.color = ft.Colors.GREEN

            self.update()

        except Exception as e:
            print(f"Erro ao verificar status do banco: {e}")


    async def em_login(self, e):
        username = self.campo_username.value.strip()
        password = self.campo_password.value.strip()

        if not username or not password:
            self.mostrar_erro("Por favor, preencha todos os campos")
            return

        self.botao_login.disabled = True
        self.texto_erro.visible = False
        self.update()

        # Verificação de credenciais
        try:
            response = await asyncio.wait_for(
                self.verificar_credenciais_async(username, password),
                timeout=10.0
            )

            if response and "access_token" in response:
                user = response["user"]
                tema_preferido = user.get("tema_preferido", "claro")

                self.page.session.set("user", user)
                self.page.session.set("token", response["access_token"])

                if tema_preferido == "escuro":
                    self.page.theme_mode = ft.ThemeMode.DARK
                else:
                    self.page.theme_mode = ft.ThemeMode.LIGHT

                self.page.update()
                self.page.go("/menu")
            else:
                self.mostrar_erro("Usuário ou senha inválidos")

        except asyncio.TimeoutError:
            self.mostrar_erro("Timeout - Verifique sua conexão")
        except Exception as ex:
            self.mostrar_erro(f"Erro ao conectar: {str(ex)}")
        finally:
            self.botao_login.disabled = False
            self.update()


    async def verificar_credenciais_async(self, username, password):
        try:
            response = await api_client.login(username, password)
            return response

        except Exception as e:
            print(f"Erro na verificação das credenciais: {e}")
            return None


    def mostrar_erro(self, message):
        self.texto_erro.value = message
        self.texto_erro.visible = True
        self.update()


    def update(self):
        self.page.update()
