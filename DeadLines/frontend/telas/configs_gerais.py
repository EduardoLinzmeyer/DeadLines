import flet as ft
import asyncio

from utils.api_client import APIClient, api_client



class TelaConfigsGerais(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        user = self.page.session.get("user")

        self.tema_original = user.get("tema_preferido", "claro") if user else "claro"

        self.titulo = ft.Text("Configurações Gerais", size=40, weight=ft.FontWeight.BOLD)

        self.switch_tema = ft.Switch(
            label="Modo Escuro",
            value=(self.tema_original == "escuro"),
            on_change=self.alt_tema
        )

        self.botao_salvar = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SAVE, size=26, color=ft.Colors.GREEN),
                    ft.Text("Salvar", size=20, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            on_click=self.salvar_tema,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            width=165,
            height=50,
            tooltip="Salvar preferências de configuração"
        )

        self.texto_mensagem = ft.Text(
            color=ft.Colors.GREEN,
            visible=False
        )

        """Layout da tela"""
        self.controls = [
            ft.Container(height=5),
            self.titulo,
            ft.Divider(height=38),
            self.texto_mensagem,
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.DARK_MODE),
                            self.switch_tema
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(height=20),
                    self.botao_salvar
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ]
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER


    def did_mount(self):
        self.resetar_tema()


    """Alterar tema"""
    def alt_tema(self, e):
        novo_tema = "escuro" if self.switch_tema.value else "claro"
        self.page.theme_mode = ft.ThemeMode.DARK if novo_tema == "escuro" else ft.ThemeMode.LIGHT
        self.page.update()


    """Salvar o tema alterado"""
    async def salvar_tema(self, e):
        user = self.page.session.get("user")
        if not user:
            self.mostrar_mensagem("Erro: Faça o login para salvar o tema.")
            return

        user_id = user["id"]
        novo_tema_bd = "escuro" if self.switch_tema.value else "claro"

        user["tema_preferido"] = novo_tema_bd
        self.page.session.set("user", user)
        self.tema_original = novo_tema_bd

        try:
            success = await api_client.alterar_tema_do_usuario(user_id,novo_tema_bd)
            if success:
                self.mostrar_mensagem("Preferência salva com sucesso")
                print(f"DEBUG: Tema '{novo_tema_bd}' salvo para usuário {user_id}")
            else:
                self.mostrar_mensagem("Erro ao salvar preferência")
                print(f"DEBUG: Falha ao salvar tema para usuário {user_id}")

        except Exception as ex:
            print(f"Erro ao salvar o tema: {ex}")
            self.mostrar_mensagem("Erro ao salvar preferência")


    def mostrar_mensagem(self, mensagem):
        self.texto_mensagem.value = mensagem
        self.texto_mensagem.visible = True
        if self.page:
            self.page.update()
        asyncio.create_task(self.esconder_mensagem())


    async def esconder_mensagem(self):
        await asyncio.sleep(1.5)
        self.texto_mensagem.visible = False
        if self.page:
            self.page.update()


    """Reversão de configs. caso não salvar"""
    def resetar_tema(self):
        self.page.theme_mode = ft.ThemeMode.DARK if self.tema_original == "escuro" else ft.ThemeMode.LIGHT
        self.switch_tema.value = (self.tema_original == "escuro")
        self.page.update()


    def voltar(self):
        self.resetar_tema()
        self.page.go("/menu")
