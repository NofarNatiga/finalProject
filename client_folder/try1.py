from types import NoneType

import flet as ft

from Requests_2 import Client


def handle_tap(e):
    print(f"handle_tap")


class Works:
    def __init__(self, page: ft.Page, client: Client):
        self.page = page
        self.page.vertical_alignment = ft.alignment.top_left
        self.client = client
        self.list1 = None
        self.image_data_info_list = None
        self.grid = None
        self.y = None

        self.anchor = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.colors.AMBER,
            bar_hint_text="Search Work...",
            on_tap=handle_tap,
            width=300,
            on_submit=self.handle_submit
        )
        list1 = client.get_all("categories")
        self.anchor.controls = [
            ft.ListTile(title=ft.Text(f" {i}"), on_click=self.close_anchor, data=i, )
            for i in list1
        ]

        self.row = ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                          controls=[
                              ft.IconButton(icon=ft.icons.SEARCH,
                                            on_click=lambda _: self.anchor.open_view()
                                            ),
                          ], )

        self.for_search = ft.Row([
            self.anchor,
            self.row, ], spacing=30, alignment=ft.MainAxisAlignment.CENTER)

        self.empty_space = ft.Container(height=10)
        self.page.add(self.empty_space, self.for_search, self.empty_space)

    def close_anchor(self, e):
        text = f"{e.control.data}"
        print(text)
        print(f"closing view from {text}")

        if self.grid is None:
            self.grid = self.create_images_grid(self.image_data_info_list)
        else:
            self.page.remove(self.grid)
            self.grid = self.create_images_grid(self.image_data_info_list)
        self.page.add(self.grid)

        self.page.update()

        self.anchor.close_view(text)

    def handle_submit(self, e):
        text = f"{e.data}"
        print("handle submit:", text)
        print(f"closing view from {text}")

        if self.grid is None:
            self.grid = self.create_images_grid(self.image_data_info_list)
        else:
            self.page.remove(self.grid)
            self.grid = self.create_images_grid(self.image_data_info_list)
        self.page.add(self.grid)

        self.page.update()

    def create_images_grid(self, image_data_info_list) -> ft.GridView:
        images_grid = ft.GridView(
            expand=1,
            runs_count=1,
            max_extent=275,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
            width=1300,
        )

        for image_info in image_data_info_list:
            if image_info["type"] == "image":
                images_grid.controls.append(
                    ft.Container(
                        width=270, height=270,
                         on_click=self.clicked(image_info),
                    )
                )
        return images_grid
