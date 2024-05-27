import flet as ft
from Add_Work import add_work
from Requests_2 import Client
from show_works import Works
# from try1 import add_work2


class NavigationBar:
    def __init__(self, page: ft.Page, client: Client):
        self.page = page
        self.page.bgcolor = "#fceee8"
        # self.page.bgcolor = "#fbf7f2"

        self.client = client

        self.page.horizontal_alignment = 'CENTER'
        self.page.vertical_alignment = 'CENTER'
        page.title = "My Virtual Art Portfolio"

        self.page_title_text = ft.Text(
            value="Home",  # Initial text value
            size=35,  # Font size
            weight=ft.FontWeight.BOLD,  # Bold text
            text_align=ft.TextAlign.LEFT,  # Centered text
            width=400
        )
        self.account_button = ft.ElevatedButton(text="Delete Account",
                                                on_click=lambda event: self.client.signout())  # bgcolor="#ff9180",
        self.starting_row = ft.Row([self.page_title_text, self.account_button], alignment=ft.alignment.top_center,
                                   vertical_alignment=ft.alignment.top_center, width=1300, spacing=825, height=100)

        self.navigation_bar = ft.NavigationBar(
            height=100,
            bgcolor="#fab9af",
            elevation=100,
            on_change=lambda e: self.change(e.control.selected_index),
            destinations=[
                ft.NavigationDestination(icon=ft.icons.HOME, label="Home", ),
                ft.NavigationDestination(icon=ft.icons.ADD, label="Add Work And Category"),
                ft.NavigationDestination(icon=ft.icons.BOOK_ROUNDED, label="Art Portfolio", ),
            ]
        )
        self.page.add(self.starting_row)
        self.page.navigation_bar = self.navigation_bar

        # show_work_instance = Works(self.page, self.client)
        # show_home_instance = Home(self.page, self.client)

    def change(self, selected_index: int):
        # Clears the current content of the page
        self.page.clean()

        # Updates the title text based on the selected index
        if selected_index == 0:
            self.page_title_text.value = "Home"
            self.page.add(self.starting_row)
        elif selected_index == 1:
            self.page_title_text.value = "Add Work Or Category"
            self.page.add(self.starting_row)
            add_work_instance = add_work(self.page, self.client)
        elif selected_index == 2:
            self.page_title_text.value = "Search your Art Portfolio"
            self.page.add(self.starting_row)
            show_work_instance = Works(self.page, self.client)
        # Adds the page title text to the page again, as it was removed in the clean() method

