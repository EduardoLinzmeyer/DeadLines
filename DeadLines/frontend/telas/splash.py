import flet as ft
import math
import asyncio



class TelaSplash(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.bgcolor = ft.Colors.WHITE10
        self._e_ativo = True

        self.barra_de_progresso = ft.ProgressBar(
            width=300,
            height=8,
            color=ft.Colors.BLUE_700,
            bgcolor=ft.Colors.BLUE_100,
            value=0,
            bar_height=10,
            border_radius=ft.border_radius.all(6)
        )

        self.texto_de_carregamento = ft.Text(
            "Iniciando DeadLines...",
            size=18,
            color=ft.Colors.GREY_700,
            weight=ft.FontWeight.BOLD
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "DeadLines",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700
                        ),
                        ft.Text(
                            "Faça a sua organização",
                            size=16,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Container(height=40),

                        # Container para a barra de progresso
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self.barra_de_progresso,
                                    ft.Container(height=15),
                                    ft.Row(
                                        controls=[
                                            self.texto_de_carregamento,
                                            ft.Container(width=10)
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=5
                                    )
                                ],
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=20)
                        ),
                        ft.Container(height=30)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.WHITE10,
                padding=30
            )
        ]

        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    """Iniciar animação quando o componente for montado"""
    def did_mount(self):
        self._e_ativo = True
        self.page.run_task(self.carregando_animacao)


    """Atualiza a página de forma segura"""
    def seguro_atualizar_pagina(self):
        try:
            if self.page and hasattr(self.page, 'update'):
                try:
                    _ = self.page.route
                    self.page.update()
                except (AttributeError, RuntimeError, Exception):
                    print("Página não está mais disponível para atualização")
                    self._e_ativo = False
        except Exception as e:
            print(f"Erro seguro ao atualizar página: {e}")


    def ease_out_quad(self, t):
        return t * (4-t)


    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - math.pow(-2 * t + 2,3) / 2


    """Animação da barra de progresso"""
    async def carregando_animacao(self):
        try:
            passos = [
                ("Iniciando...", 0.2),
                ("Conectando ao bando de dados...", 0.4),
                ("Carregando configurações...", 0.6),
                ("Preparando interface...", 0.8),
                ("Pronto!", 1.0)
            ]

            duracao_total = 4.0
            frames_por_passo = 60

            for texto_passo, valor_alvo in passos:
                if not self._e_ativo:
                    return

                self.texto_de_carregamento.value = texto_passo
                valor_atual = self.barra_de_progresso.value or 0

                for frame in range(frames_por_passo):
                    if not self._e_ativo:
                        return

                    progresso = frame / (frames_por_passo - 1)
                    eased_progresso = self.ease_in_out_cubic(progresso)
                    novo_valor = valor_atual + (valor_alvo - valor_atual) * eased_progresso

                    self.barra_de_progresso.value = novo_valor

                    if frame % 3 == 0:
                        try:
                            self.page.update()
                        except Exception as e:
                            print(f"Erro ao atualizar a página: {e}")
                            return

                    await asyncio.sleep(duracao_total / (len(passos) * frames_por_passo * 2.5))

                if self._e_ativo:
                    self.barra_de_progresso.value = valor_alvo
                    self.page.update()

            if self._e_ativo:
                await asyncio.sleep(0.5)
                self.page.go("/menu")

        except asyncio.CancelledError:
            print("Animação do splash cancelada")
        except Exception as e:
            print(f"Erro na animação do splash: {e}")
            if self._e_ativo:
                try:
                    self.barra_de_progresso.value = 1.0
                    self.texto_de_carregamento = "Carregamento concluído!"
                    self.page.update()
                    await asyncio.sleep(0.5)
                    self.page.go("/menu")
                except Exception as e:
                    print(f"Erro ao navegar para o menu: {e}")


    """Parar animação quando o componente for desmontado"""
    def will_unmount(self):
        self._e_ativo = False
