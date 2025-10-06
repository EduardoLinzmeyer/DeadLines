import flet as ft
import asyncio
import os



class MainMenu(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        """Componentes do menu principal"""
        self.titulo = ft.Text("DeadLines", size=40, weight=ft.FontWeight.BOLD)

        self.botao_abrir_agendamentos = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SCHEDULE, size=26),
                    ft.Text("Agendamentos", size=22)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            on_click=lambda _: self.ir_para_agendamentos(),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=250,
            height=45,
        )

        self.botao_abrir_listas = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LIST, size=26),
                    ft.Text("Listas", size=22)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            on_click=lambda _: self.ir_para_listas(),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=250,
            height=45,
        )

        self.botao_relatorios = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ANALYTICS, size=26),
                    ft.Text("Relatórios", size=22)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            on_click= lambda _: self.ir_para_relatorios(),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=250,
            height=45,
        )

        self.botao_configs = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SETTINGS, size=26),
                    ft.Text("Configurações", size=22)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            on_click=lambda _: self.ir_para_configs(),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=250,
            height=45,
        )

        self.botao_logout = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text="Confirmar saída",
                    icon=ft.Icons.LOGOUT,
                    on_click=self.fazer_logout
                )
            ],
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LOGOUT,size=25, color=ft.Colors.RED_700),
                        ft.Text("Sair", size=22, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ),
                width=145,
                height=50,
                border_radius=20,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                padding=5,
                alignment=ft.alignment.center
            ),
            tooltip="Fazer logout"
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

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(expand=True),
                        ft.Column(
                            controls=[
                                ft.Container(height=30),
                                self.titulo,
                                ft.Container(height=90),
                                self.botao_abrir_agendamentos,
                                ft.Container(height=30),
                                self.botao_abrir_listas,
                                ft.Container(height=30),
                                self.botao_relatorios,
                                ft.Container(height=30),
                                self.botao_configs,
                                ft.Container(height=120),
                                self.botao_logout,
                                ft.Container(height=100),
                                self.info_usuario,
                                ft.Container(height=15)
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Container(expand=True)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                expand=True
            )
        ]

        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    def ir_para_agendamentos(self):
        self.page.go("/agendamentos")


    def ir_para_listas(self):
        self.page.go("/listas")


    def ir_para_relatorios(self):
        self.page.go("/relatorios")


    def ir_para_configs(self):
        self.page.go("/configs")


    def fazer_logout(self, e):
        self.page.session.remove("user")
        self.page.go("/login")
