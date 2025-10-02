import flet as ft

from telas.agendamentos_home import TelaAgendamentosHome
from telas.agendamentos_calendario import TelaAgendamentosCalendario
from telas.agendamentos_clientes import TelaAgendamentosClientes
from telas.agendamentos_servicos import TelaAgendamentosServicos



class TelaAgendamentos(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        self.titulo = ft.Text("Agendamentos", size=36, weight=ft.FontWeight.BOLD)

        """Contâiner para o conteúdo"""
        self.conteudo_submenu = ft.Column(
            expand=True
        )

        """Botões principais"""
        self.botao_home = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.HOME, size=26),
                    ft.Text("Home", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=lambda e: self.mostrar_submenu(TelaAgendamentosHome(self.page)),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Início"
        )

        self.botao_calendario_agendamentos = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=26),
                    ft.Text("Calendário", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=lambda e: self.mostrar_submenu(TelaAgendamentosCalendario(self.page)),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Agendamentos mensais"
        )

        self.botao_clientes = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=26),
                    ft.Text("Clientes", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=lambda e: self.mostrar_submenu(TelaAgendamentosClientes(self.page)),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Cadastro de clientes"
        )

        self.botao_servicos = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.HANDYMAN, size=26),
                    ft.Text("Serviços", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=lambda e: self.mostrar_submenu(TelaAgendamentosServicos(self.page)),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Cadastro de serviços"
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
                            color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
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
                                    self.botao_home,
                                    self.botao_calendario_agendamentos,
                                    self.botao_clientes,
                                    self.botao_servicos,
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
        # Abrir Agendamentos em Home
        self.mostrar_submenu(TelaAgendamentosHome(self.page))


    """Responsável por limpar o conteúdo atual e adicionar o novo submenu, atualizando a interface"""
    def mostrar_submenu(self, view):
        self.conteudo_submenu.controls.clear()
        self.conteudo_submenu.controls.append(view)
        self.page.update()
