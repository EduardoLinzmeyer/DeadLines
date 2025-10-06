import flet as ft

from telas.relatorios_home import TelaRelatoriosHome



class TelaRelatorios(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        """Contâiner para o conteúdo"""
        self.conteudo_submenu = ft.Column(
            expand=True
        )

        self.titulo = ft.Text("Relatórios", size=32, weight=ft.FontWeight.BOLD)

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
            on_click=lambda e: self.mostrar_submenu(TelaRelatoriosHome(self.page)),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=300,
            height=60,
            tooltip="Início"
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
            tooltip="Voltar para o menu inicial"
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
                                    self.botao_home
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
        self.mostrar_submenu(TelaRelatoriosHome(self.page))


    """Responsável por limpar o conteúdo atual e adicionar o novo submenu, atualizando a interface"""
    def mostrar_submenu(self, view):
        self.conteudo_submenu.controls.clear()
        self.conteudo_submenu.controls.append(view)
        self.page.update()
