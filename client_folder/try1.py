from types import NoneType

import flet as ft

from Requests_2 import Client


def handle_tap(e):
    print(f"handle_tap")


def bs_dismissed(e):
    print("Dismissed!")


class Works:
    def __init__(self, page: ft.Page, client: Client):
        self.sheet_content = ft.Text(value="")
        self.page = page
        self.page.vertical_alignment = ft.alignment.top_left
        self.client = client
        self.list1 = None
        self.image_data_info_list = None
        self.grid = None
        self.y = None

        self.search_in = ft.Dropdown(
            label="Search Public Works/ Your Portfolio", border_radius=40, width=300, hint_text="choose",
            options=[
                ft.dropdown.Option("public"),
                ft.dropdown.Option("private")
            ]
        )

        self.options = ft.Dropdown(
            label="Filter By", border_radius=40,
            # on_change=self.handle_options,
            hint_text="Choose a filter",
            width=300,
            options=[
                ft.dropdown.Option("Title"),
                ft.dropdown.Option("Category"),
                ft.dropdown.Option("Date"),
                ft.dropdown.Option("Rating"),
            ],
        )

        self.anchor = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.colors.AMBER,
            bar_hint_text="Search Work...",
            on_tap=handle_tap,
            width=300,
            # on_submit=self.handle_submit
        )

        self.row = ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                          controls=[
                              ft.IconButton(icon=ft.icons.SEARCH,
                                            on_click=lambda _: self.anchor.open_view()
                                            ),
                          ], )

        self.for_search = ft.Row([self.search_in, self.options,
                                  self.anchor,
                                  self.row, ], spacing=30, alignment=ft.MainAxisAlignment.CENTER)

        self.empty_space = ft.Container(height=10)

        self.page.add(self.empty_space, self.for_search, self.empty_space)


