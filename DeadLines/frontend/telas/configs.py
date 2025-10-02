import asyncio
import flet as ft

from telas.configs_gerais import TelaConfigsGerais
from telas.controle_usuarios import TelaControleUsuarios
from utils.api_client import api_client



class TelaConfig(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        self.titulo = ft.Text("Configurações", size=36, weight=ft.FontWeight.BOLD)

        """Contâiner para o conteúdo dinâmico do submenu"""
        self.conteudo_submenu = ft.Column(
            expand=True,
        )

        """Botão dos Submenus"""
        self.botao_gerais = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SETTINGS, size=26),
                    ft.Text("Configurações Gerais", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=self.mostrar_submenu_gerais,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60
        )

        self.botao_usuarios = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PEOPLE_ALT, size=26),
                    ft.Text("Controle de Usuários", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=self.mostrar_submenu_usuarios,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60
        )

        self.botao_voltar = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ARROW_BACK, size=30),
                    ft.Text("Voltar", size=24, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=30,
            ),
            on_click=lambda e: self.page.go("/menu"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Voltar para o Menu"
        )

        user = self.page.session.get("user")

        self.info_usuario = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON, size=20, color=ft.Colors.BLUE_700),
                ft.Column(
                    controls=[
                        ft.Text(
                            f"{user['nome_completo']} ({user['username']})",
                            size=14
                        ),
                        ft.Text(
                            f"Nível de Acesso: {user['nivel_acesso_nome']}",
                            size=12,
                            color=ft.Colors.SURFACE_CONTAINER_HIGHEST
                        ),
                    ],
                    spacing=1,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            visible=True if user else False
        )

        """Layout da tela"""
        self.controls = [
            ft.Row(
                expand=True,
                controls=[
                    ft.Column(
                        [
                            # Parte de cima (título + botões principais)
                            ft.Column(
                                [
                                    ft.Container(height=2),
                                    self.titulo,
                                    ft.Divider(),
                                    self.botao_gerais,
                                    self.botao_usuarios,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),

                            # Parte de baixo (botão voltar + usuário)
                            ft.Column(
                                [
                                    self.botao_voltar,
                                    self.info_usuario,
                                    ft.Container(height=5)
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # distribui topo e rodapé
                        width=350
                    ),
                    ft.VerticalDivider(width=1),
                    self.conteudo_submenu
                ]
            )
        ]


    def did_mount(self):
        self.page.run_task(self.mostrar_submenu, TelaConfigsGerais(self.page))


    async def mostrar_submenu_gerais(self, e):
        await self.mostrar_submenu(TelaConfigsGerais(self.page))


    async def mostrar_submenu_usuarios(self, e):
        await self.mostrar_submenu(TelaControleUsuarios(self.page))


    """Responsável por limpar o conteúdo atual e adicionar o novo submenu, atualizando a interface"""
    async def mostrar_submenu(self, view):
        user_token = self.page.session.get("token")
        if user_token:
            api_client.token = user_token

        self.conteudo_submenu.controls.clear()
        self.conteudo_submenu.controls.append(view)
        self.page.update()
