import flet as ft
from Requests_2 import Client
from signup_login_card import Login_Signup_Card


class App1:
    def __init__(self, url: str) -> None:
        self.page = None
        self.client = Client(url)
        self.card = None

    def main(self, page: ft.Page) -> None:
        self.page = page
        self.page.theme = ft.Theme(color_scheme_seed="#ff9180")

        # self.page.theme_mode = "dark"

        self.page.horizontal_alignment = 'CENTER'
        self.page.vertical_alignment = 'CENTER'

        if self.client.name is None and self.client.password is None:
            self.card = Login_Signup_Card(self.page, self.client).card
            self.page.update()
            self.page.add(self.card)


def main() -> None:
    ft.app(target=App1("http://127.0.0.1:6666").main)


if __name__ == "__main__":
    main()
