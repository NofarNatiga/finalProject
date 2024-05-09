import flet as ft
from Requests_2 import Client
from time import sleep
from navigator import NavigationBar


class Login_Signup_Card:
    def __init__(self, page: ft.Page, client: Client):
        self.page = page
        self.client = client
        color1 = "#FF9393"
        color2 = "WHITE"
        color3 = "#FEE1DA"

        self.login_button = ft.ElevatedButton("Log in", on_click=self.login, color="black", bgcolor=color1)
        self.signup_button = ft.ElevatedButton("Sign up", on_click=self.sign_up, color="black", bgcolor=color1)

        self.name = ft.TextField(label="Name", filled=True, width=270, height=40, bgcolor=color2
                                 )
        self.password = ft.TextField(label="Password", height=40, filled=True,
                                     can_reveal_password=True, width=270, password=True, bgcolor=color2)

        self.phone = ft.TextField(label="Phone Number", filled=True, width=270, height=40, bgcolor=color2
                                  )

        self.content = ft.Column([self.name, self.password, self.phone], alignment=ft.MainAxisAlignment.CENTER)

        self.response = ft.TextField(border_width=0.1, read_only=True, width=250, height=40)

        self.card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.ACCOUNT_CIRCLE),
                            title=ft.Text("Login or Sign up"),
                            subtitle=ft.Text(
                                "Log in to your art proto-folio account or create an account if you don't already have one "
                            ),
                        ),
                        ft.Row([self.content], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([self.response], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row(
                            [self.login_button, self.signup_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ], spacing=40
                ),
                width=500, padding=10, height=500, gradient=ft.RadialGradient([color3])
            ), elevation=20,
        )

    def login(self, e: ft.ControlEvent):
        name = self.name.value
        password = self.password.value

        response, j_response = self.client.authenticate(name, password)

        self.response.value = j_response["response"]
        self.response.text_align = 'CENTER'

        self.page.update()

        if self.client.name is not None:
            sleep(1)
            self.page.remove(self.card)
            self.page.bar = NavigationBar(self.page, self.client)
            self.page.update()

    def sign_up(self, e: ft.ControlEvent):
        name = self.name.value
        password = self.password.value

        response, j_response = self.client.signup(name, password)
        self.response.value = j_response["response"]
        self.response.text_align = 'CENTER'

        self.page.update()

        if self.client.name is not None:
            sleep(1)
            self.page.remove(self.card)
            self.page.bar = NavigationBar(self.page, self.client)
            self.page.update()
