import flet as ft
import asyncio

from utils.api_client import APIClient, api_client



class TelaListasHome(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        user = self.page.session.get("user")

        self.titulo = ft.Text("Home", size=40, weight=ft.FontWeight.BOLD)

        # Mensagem qualquer para pós implementação
        self.mensagem = ft.Text("Aqui ficará o Home de Listas.")

        """Layout da tela"""
        self.controls = [
            ft.Container(height=5),
            self.titulo,
            ft.Divider(height=38),
            ft.Column(
                [
                    ft.Row(
                        [
                            self.mensagem
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
