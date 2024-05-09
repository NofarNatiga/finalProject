import flet as ft
import requests
from time import sleep


class Client:
    def __init__(self, url):
        self.super_admin = None
        self.name = None
        self.password = None
        self.server_address = url

    def authenticate_admin(self, name, password, super_admin):
        credentials = {"name": name, "password": password, "super_admin": super_admin}
        response_ = requests.post(
            f"{self.server_address}/authenticate_admin",
            json=credentials
        )
        print(response_, response_.json())

        if response_.json()["response"].lower() == "user authenticated":
            self.name = name
            self.password = password
            self.super_admin = super_admin

        return response_, response_.json()

    def block(self, username):
        credentials = {"name": self.name, "password": self.password, "super_admin": self.super_admin}
        params = {"user": username}
        response_ = requests.post(
            f"{self.server_address}/block",
            json=credentials,
            params=params
        )

        return response_, response_.json()

    def for_gui(self):
        credentials = {"name": self.name, "password": self.password, "super_admin": self.super_admin}
        response = requests.get(
            f"{self.server_address}/for_gui",
            json=credentials

        )
        return response, response.json()


class App_1:
    def __init__(self, name_and_space, page: ft.Page, client: Client):
        self.name_and_space = name_and_space
        self.client = client
        print(name_and_space)
        self.page = page
        self.page.vertical_alignment = ft.alignment.top_center
        for i in self.name_and_space:
            color = ft.colors.BLUE
            if i["size"]["data"] > 3:
                color = "#ff2100"
            r = ft.ExpansionTile(
                title=ft.Text("User : " + i["name"]),
                icon_color=color,
                collapsed_icon_color=color,
                subtitle=ft.Text("Trailing expansion arrow icon"),
                affinity=ft.TileAffinity.PLATFORM,
                initially_expanded=False,
                maintain_state=True,
                controls=[
                    ft.ListTile(title=ft.Text(i["size"]["text"]),
                                trailing=ft.IconButton(icon=ft.icons.BLOCK_SHARP, icon_color=color),
                                on_click=self.clicked(i["name"]), tooltip="Block from adding more")]
            )
            self.page.add(r)
        self.page.update()

    def clicked(self, username: str):
        self.client.block(username)


class Login_Signup_Card_2:
    def __init__(self, page: ft.Page, client: Client):
        self.page = page
        self.client = client

        self.login_button = ft.ElevatedButton("Log in", on_click=self.login)
        self.signup_button = ft.ElevatedButton("Sign up", on_click=self.sign_up, )

        self.name = ft.TextField(label="Name", filled=True, width=270, height=40,
                                 )
        self.password = ft.TextField(label="Password", height=40, filled=True,
                                     can_reveal_password=True, width=270, password=True)

        # self.phone = ft.TextField(label="Phone Number", filled=True, width=270, height=40
        #                           )
        self.c2 = ft.Checkbox(label="super admin", value=False)

        self.content = ft.Column([self.name, self.password, self.c2], alignment=ft.MainAxisAlignment.CENTER)

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
                width=500, padding=10, height=500,
            ), elevation=20,
        )

    def login(self, e: ft.ControlEvent):
        name = self.name.value
        password = self.password.value

        response, j_response = self.client.authenticate_admin(name, password, self.c2.value)

        self.response.value = j_response["response"]
        self.response.text_align = 'CENTER'

        self.page.update()

        if self.client.name is not None:
            sleep(1)
            self.page.remove(self.card)
            _, j_response = self.client.for_gui()
            if j_response["response"] == "success":
                App_1(j_response["data"], self.page, self.client)

            print(j_response)

    def sign_up(self, e: ft.ControlEvent):
        name = self.name.value
        password = self.password.value

        # response, j_response = self.client.signup(name, password)
        # self.response.value = j_response["response"]
        # self.response.text_align = 'CENTER'
        #
        # self.page.update()
        #
        # if self.client.name is not None:
        #     sleep(1)
        #     self.page.remove(self.card)
        #     self.page.bar = NavigationBar(self.page, self.client)
        #     self.page.update()


class App_3:
    def __init__(self, url: str) -> None:
        self.page = None
        self.client = Client(url)
        self.card = None

    def main(self, page: ft.Page) -> None:
        self.page = page
        self.page.window_height = 700
        self.page.window_width = 700
        self.page.theme_mode = "dark"

        self.page.horizontal_alignment = 'CENTER'
        self.page.vertical_alignment = 'CENTER'

        if self.client.name is None and self.client.password is None:
            self.card = Login_Signup_Card_2(self.page, self.client).card
            self.page.update()
            self.page.add(self.card)


def main() -> None:
    ft.app(target=App_3("http://10.0.0.22:6666").main)


if __name__ == "__main__":
    main()
