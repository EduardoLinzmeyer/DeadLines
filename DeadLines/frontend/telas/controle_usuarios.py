import flet as ft
import asyncio
import sys
import pathlib

from utils.api_client import APIClient, api_client

current_dir = pathlib.Path(__file__).parent
utils_path = current_dir.parent.parent / "utils"
sys.path.append(str(utils_path))



class TelaControleUsuarios(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.user = self.page.session.get("user")
        self.token = self.page.session.get("token")
        if self.token:
            api_client.token = self.token


        self.tema_original = self.user.get("tema_preferido", "claro") if self.user else "claro"

        self.titulo = ft.Text("Controle de Usuários", size=40, weight=ft.FontWeight.BOLD)

        self.tabela_usuarios = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Usuário")),
                ft.DataColumn(ft.Text("Nome Completo")),
                ft.DataColumn(ft.Text("Nível de Acesso")),
                ft.DataColumn(ft.Text("Ativo")),
            ],
            rows=[]
        )

        """Checagem de nível de acesso"""
        if not self.user or self.user.get("nivel_acesso_id") != 1:
            self.conteudo_principal = ft.Column(
                [
                    ft.Text(
                        "Acesso negado. Você não tem permissão para visualizar esta página.",
                        size=20,
                        color=ft.Colors.RED_500,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        else:
            # Tabela de usuários
            self.conteudo_principal = ft.Column(
                [
                    ft.Row([self.tabela_usuarios], scroll=ft.ScrollMode.ADAPTIVE)
                ],
                expand=True
            )

        """Layout da tela"""
        self.controls = [
            ft.Container(height=5),
            self.titulo,
            ft.Divider(height=38),
            ft.Column(
                [
                    ft.Row(
                        [
                            self.conteudo_principal
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    def did_mount(self):
        self.resetar_tema()

        if self.user and self.user.get("nivel_acesso_id") == 1:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(self.carregar_usuarios())


    """Resetar tema quando alterações não forem salvas"""
    def resetar_tema(self):
        self.page.theme_mode = ft.ThemeMode.DARK if self.tema_original == "escuro" else ft.ThemeMode.LIGHT
        self.page.update()


    async def carregar_usuarios(self):
        usuarios_data = await api_client.get_users()
        print("DEBUG: Usuarios retornados:", usuarios_data)

        if usuarios_data:
            self.tabela_usuarios.rows.clear()
            for user in usuarios_data:
                self.tabela_usuarios.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(user['id']))),
                            ft.DataCell(ft.Text(user['username'])),
                            ft.DataCell(ft.Text(user['nome_completo'])),
                            ft.DataCell(ft.Text(user['nivel_acesso'])),
                            ft.DataCell(
                                ft.Icon(
                                    ft.Icons.CHECK if user['ativo'] else ft.Icons.CLOSE,
                                    color=ft.Colors.GREEN if user['ativo'] else ft.Colors.RED
                                )
                            ),
                        ]
                    )
                )

            self.page.update()
        else:
            print("DEBUG: Nenhum usuário retornado ou erro na API.")
