import asyncio
import logging
import sys
import pathlib
import flet as ft
import httpx

from telas.login import TelaLogin
from telas.splash import TelaSplash
from telas.menu import MainMenu
from telas.agendamentos import TelaAgendamentos
from telas.configs import TelaConfig
from utils.api_client import api_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_dir = pathlib.Path(__file__).parent
sys.path.append(str(current_dir))



"""Testar conexão com API"""
async def testar_conexao_api(page):
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            response = await api_client.conexao_teste()
            if response and response.get("message") == "API Backend OK":
                print("DEBUG: Conexão com a API bem sucedida")
                page.session.set("api_conectada", "true")
                return True
            print(f"Tentativa {tentativa + 1}: API não respondeu corretamente")

        except (httpx.RequestError, ValueError) as error:
            print(f"Tentativa {tentativa + 1}: Erro ao conectar - {error}")

        await asyncio.sleep(1)  # Aguarda entre tentativas

    page.session.set("api_conectada", "false")
    print("Aviso: Não foi possível conectar a API após várias tentativas")
    return False


"""Roteamento de telas"""
async def alt_rotas(e):
    global page
    try:
        page = e.page
        page.views.clear()


        if page.route == "/":
            splash = TelaSplash(page)
            page.views.append(
                ft.View(
                    "/",
                    [splash],
                    padding=0,
                    spacing=0,
                    bgcolor=ft.Colors.WHITE10
                )
            )
            page.update()

            await testar_conexao_api(page)
            await asyncio.sleep(2)
            page.go("/login")


        elif page.route == "/login":
            page.theme_mode = ft.ThemeMode.LIGHT
            api_status = page.session.get("api_conectada")
            login = TelaLogin(page)

            login_controls = [login]

            if api_status == "false":
                login_controls.insert(0, ft.AlertDialog(
                    title=ft.Text("Aviso"),
                    content=ft.Text("Modo offline"),
                    open=True
                ))

            login_view = ft.View(
                "/login",
                login_controls,
                bgcolor=ft.Colors.SURFACE
            )
            page.views.append(login_view)


        elif page.route == "/menu":
            user = page.session.get("user")
            if not user:
                page.go("/login")
                return

            tema_preferido = user.get("tema_preferido", "claro")
            page.theme_mode = ft.ThemeMode.DARK if tema_preferido == "escuro" else ft.ThemeMode.LIGHT
            page.update()

            menu = MainMenu(page)
            page.views.append(
                ft.View(
                    "/menu",
                    [menu],
                    bgcolor=ft.Colors.SURFACE
                )
            )


        elif page.route == "/agendamentos":
            if not page.session.get("user"):
                page.go("/login")
                return

            agendamentos_view = ft.View(
                "/agendamentos",
                [TelaAgendamentos(page)],
                bgcolor=ft.Colors.SURFACE
            )
            page.views.append(agendamentos_view)


        elif page.route == "/configs":
            if not page.session.get("user"):
                page.go("/login")
                return

            configs_view = ft.View(
                "/configs",
                [TelaConfig(page)],
                bgcolor=ft.Colors.SURFACE
            )
            page.views.append(configs_view)


        page.update()

    except (ValueError, KeyError, AttributeError) as error:
        logger.error("Erro no roteamento: %s", error)
        page.go("/login")


def visualizacao_pop(e):
    if len(page.views) > 1:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


async def main(page: ft.Page):
    page.title = "DeadLines - Faça sua a organização"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_700)
    page.window.resizable = True
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.bgcolor = ft.Colors.SURFACE

    page.session.set("api_conectada", "false")

    user = page.session.get("user")
    if user and "tema_preferido" in user:
        page.theme_mode = user['tema_preferido']
    else:
        page.theme_mode = ft.ThemeMode.LIGHT


    page.on_route_change = alt_rotas
    page.on_view_pop = visualizacao_pop

    page.go("/")




if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets",
        web_renderer="canvaskit"
    )

"""Executar separadamente em ambiente de Desenvolvimento"""
"""
    Para backend: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    Para frontend: python main.py
"""