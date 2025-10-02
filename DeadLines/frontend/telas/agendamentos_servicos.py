import flet as ft

from utils.api_client import APIClient, api_client


class TelaAgendamentosServicos(ft.Row):  # Row para dividir horizontalmente
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.servico_editando = None
        self.checkboxes_servicos = []
        self.checkbox_marcar_todos = None

        user = self.page.session.get("user")

        self.titulo = ft.Text("Serviços", size=40, weight=ft.FontWeight.BOLD)

        # Área de listagem (70%)
        self.area_listagem = self.criar_area_listagem()

        # Área de edição (30%) - inicialmente vazia
        self.area_edicao = self.criar_area_edicao()
        self.area_edicao.visible = False

        """Layout principal dividido"""
        self.controls = [
            ft.Container(
                content=self.area_listagem,
                expand=7,
                padding=10
            ),
            ft.VerticalDivider(width=1),
            ft.Container(
                content=self.area_edicao,
                expand=3,
                padding=10,
                bgcolor=ft.Colors.SURFACE
            )
        ]

        # Carregar dados iniciais
        self.carregar_servicos()


    def criar_area_listagem(self):
        # Botão para adicionar novo serviço
        self.botao_adicionar = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD),
                    ft.Text("Novo Serviço")
                ],
                tight=True
            ),
            on_click=self.novo_servico,
            bgcolor=ft.Colors.GREEN
        )

        self.checkbox_marcar_todos = ft.Checkbox(
            label="Marcar todos",
            on_change=self.alternar_marcar_todos
        )

        # Lista de serviços
        self.lista_servicos = ft.ListView(
            expand=True,
            spacing=10,
            padding=20
        )

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(height=5),
                        self.titulo,
                        ft.Divider(height=73),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        self.checkbox_marcar_todos,
                        self.botao_adicionar
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                self.lista_servicos
            ],
            expand=True
        )


    def criar_area_edicao(self):
        # Campos do formulário
        self.campo_nome = ft.TextField(
            label="Nome do Serviço",
            prefix_icon=ft.Icons.DESIGN_SERVICES,
            expand=True
        )

        self.campo_descricao = ft.TextField(
            label="Descrição",
            prefix_icon=ft.Icons.DESCRIPTION,
            multiline=True,
            min_lines=3,
            max_lines=5
        )

        self.campo_valor = ft.TextField(
            label="Valor (R$)",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.campo_duracao = ft.TextField(
            label="Duração (minutos)",
            prefix_icon=ft.Icons.ACCESS_TIME,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Botões de ação
        self.botoes_acao = ft.Row(
            controls=[
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SAVE, size=24, color=ft.Colors.BLUE),
                            ft.Text("Salvar", size=20, weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    on_click=self.salvar_servico,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    width=160,
                    height=50
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Confirmar cancelamento",
                            icon=ft.Icons.CANCEL,
                            on_click=self.cancelar_edicao
                        )
                    ],
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CANCEL, size=24, color=ft.Colors.RED_900),
                                ft.Text("Cancelar", size=20, weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        width=160,
                        height=50,
                        border_radius=30,
                        padding=0,
                        alignment=ft.alignment.center
                    ),
                    tooltip="Cancelar edição"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=5
        )

        return ft.Column(
            controls=[
                ft.Text("Editar Serviço", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.campo_nome,
                self.campo_descricao,
                ft.Row([self.campo_valor, self.campo_duracao]),
                self.botoes_acao
            ],
            spacing=20
        )


    def carregar_servicos(self):
        # Por enquanto, dados de exemplo
        servicos_exemplo = [
            {"id": 1, "nome": "Corte de Cabelo", "descricao": "Corte masculino", "valor": 30.00, "duracao": 30},
            {"id": 2, "nome": "Barba", "descricao": "Aparar e modelar barba", "valor": 20.00, "duracao": 20},
            {"id": 3, "nome": "Corte e Barba", "descricao": "Pacote completo", "valor": 45.00, "duracao": 50}
        ]

        self.lista_servicos.controls.clear()
        self.checkboxes_servicos.clear()

        for servico in servicos_exemplo:
            checkbox = ft.Checkbox(
                on_change=self.atualizar_checkbox_marcar_todos
            )
            self.checkboxes_servicos.append(checkbox)

            item = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            checkbox,
                            ft.Container(
                                content=ft.ListTile(
                                    leading=ft.Icon(ft.Icons.DESIGN_SERVICES),
                                    title=ft.Text(servico["nome"]),
                                    subtitle=ft.Text(f"R$ {servico['valor']} - {servico['duracao']}min"),
                                ),
                                expand=True
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                on_click=lambda e, s=servico: self.editar_servico(s)
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    padding=10
                )
            )
            self.lista_servicos.controls.append(item)

        self.page.update()


    def alternar_marcar_todos(self, e):
        marcar = self.checkbox_marcar_todos.value
        for checkbox in self.checkboxes_servicos:
            checkbox.value = marcar
        self.page.update()


    """Se todos estiverem marcados ativa MARCAR TODOS e se algum estiver desmarcado desativa"""
    def atualizar_checkbox_marcar_todos(self, e):
        todos_marcados = all(checkbox.value for checkbox in self.checkboxes_servicos)
        self.checkbox_marcar_todos.value = todos_marcados
        self.page.update()


    """Prepara o formulário para um novo serviço"""
    def novo_servico(self, e):
        self.servico_editando = None
        self.limpar_formulario()
        self.area_edicao.visible = True
        self.page.update()


    """Preenche o formulário com dados do serviço para edição"""
    def editar_servico(self, servico):
        self.servico_editando = servico
        self.campo_nome.value = servico["nome"]
        self.campo_descricao.value = servico["descricao"]
        self.campo_valor.value = str(servico["valor"])
        self.campo_duracao.value = str(servico["duracao"])
        self.area_edicao.visible = True
        self.page.update()


    def limpar_formulario(self):
        self.campo_nome.value = ""
        self.campo_descricao.value = ""
        self.campo_valor.value = ""
        self.campo_duracao.value = ""


    async def salvar_servico(self, e):
        if not self.campo_nome.value:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Nome do serviço é obrigatório!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            # Preparar dados
            dados_servico = {
                "nome": self.campo_nome.value,
                "descricao": self.campo_descricao.value,
                "valor": float(self.campo_valor.value or 0),
                "duracao": int(self.campo_duracao.value or 0)
            }

            if self.servico_editando:
                print(f"Atualizando serviço: {dados_servico}")
            else:
                print(f"Criando novo serviço: {dados_servico}")

            # Recarregar lista e limpar formulário
            self.carregar_servicos()
            self.limpar_formulario()
            self.servico_editando = None

            self.page.snack_bar = ft.SnackBar(content=ft.Text("Serviço salvo com sucesso!"))
            self.page.snack_bar.open = True

        except ValueError:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Valor e duração devem ser números!"))
            self.page.snack_bar.open = True

        self.page.update()


    def cancelar_edicao(self, e):
        self.limpar_formulario()
        self.servico_editando = None
        self.area_edicao.visible = False
        self.page.update()

