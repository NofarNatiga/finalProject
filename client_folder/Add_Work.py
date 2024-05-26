import flet as ft
import base64
from Requests_2 import Client

from datetime import datetime
import logging
import io
from fastapi import UploadFile


def bs_dismissed(e):
    print("Dismissed!")


class add_work:
    def __init__(self, page: ft.Page, client: Client) -> None:
        self.file_extension = None
        self.video_data = None
        self.page = page
        border_r = 5
        self.page.scroll = "always"
        height = 60
        width = 350
        # field_color = "#FFF0E1"
        field_color = ft.colors.WHITE
        button_color = "#ff9180"

        self.page.horizontal_alignment = 'CENTER'
        self.page.vertical_alignment = 'CENTER'

        self.client = client
        self.button_pick = None
        self.all = None

        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result, )

        self.pick_files_dialog.FilePickerFileType = "IMAGE"
        self.selected_files = ft.Text(width=width, height=height)

        self.image_container = ft.Container(height=400, width=300, bgcolor=ft.colors.WHITE, border_radius=10,
                                            border=ft.border.all(2, "black")

                                            )

        self.title = ft.TextField(label='title', width=width, height=height, bgcolor=field_color,
                                  border_radius=border_r)
        self.category_names = ft.TextField(label='categories', width=width / 2, height=height, bgcolor=field_color,
                                           border_radius=border_r)

        response, response_j = self.client.get_all("category")
        list1 = []
        print(response_j)
        if response_j["response"] == "success":
            list1 = response_j["data"]

        self.category_names2 = ft.SearchBar(bar_hint_text="Add Category...",
                                            view_hint_text="Add a Category...",
                                            width=width / 2, on_submit=lambda _: self.submit_search,
                                            view_shape=ft.ContinuousRectangleBorder(radius=1),
                                            bar_bgcolor=ft.colors.WHITE,
                                            view_bgcolor=ft.colors.WHITE, controls=[
                ft.ListTile(title=ft.Text(f" {i}"), on_click=self.click_search, data=i)
                for i in list1
            ])

        self.description = ft.TextField(label='description', width=width, height=height, bgcolor=field_color,
                                        border_radius=border_r)
        self.share_with = ft.TextField(label='Share With...', width=width, height=height, bgcolor=field_color,
                                       border_radius=border_r)
        self.rating = ft.Slider(min=0, max=100, divisions=100, label="{value}%", width=width)
        self.public = ft.Switch(label="public", value=False, label_position=ft.LabelPosition.LEFT, )

        self.save = ft.ElevatedButton("save", on_click=self.saved, bgcolor=button_color, color=ft.colors.WHITE
                                      )

        self.file_data = None

        self.page.overlay.append(self.pick_files_dialog)
        self.button_pick = ft.ElevatedButton(
            "Pick file",
            icon=ft.icons.UPLOAD_FILE, width=300, style=ft.ButtonStyle(
                bgcolor="#ff9180", color=ft.colors.WHITE
            ),
            on_click=lambda _: self.pick_files_dialog.pick_files(
            ))

        self.name = ft.TextField(label='Category Name', width=width, height=height, bgcolor=field_color,
                                 border_radius=border_r)
        self.category_description = ft.TextField(label='Description', width=width, height=height, bgcolor=field_color,
                                                 border_radius=border_r)

        self.save2 = ft.ElevatedButton("save", on_click=self.saved2, bgcolor=button_color, color=ft.colors.WHITE
                                       )

        self.empty = ft.Row(height=6)

        self.layout = ft.Row([ft.Column([], width=60),
                              ft.Column([self.image_container, self.button_pick]),
                              ft.Column([self.title, self.description, self.share_with,
                                         ft.Row([self.category_names, self.category_names2]), self.rating,
                                         self.public,
                                         ], spacing=20, alignment=ft.alignment.center), ft.Column([], width=60),
                              ft.Column([self.name, self.category_description, ft.Container(height=290)])],
                             spacing=50,
                             alignment=ft.alignment.center, width=1000, )

        self.titles = ft.Row(
            [ft.Column(width=400), ft.Text(value="Add Work", weight=ft.FontWeight.BOLD, size=15), ft.Column(width=600),
             ft.Text(value="Add Category", weight=ft.FontWeight.BOLD, size=15)])

        self.sheet_content = ft.Text()

        self.bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        self.sheet_content,
                        ft.ElevatedButton("OK, close sheet", on_click=self.close_bs),
                    ],
                    tight=True,
                ),
                padding=10,
            ),
            open=False,
            on_dismiss=bs_dismissed
        )

        self.page.add(
            ft.Column([self.empty, self.titles, self.layout,
                       ft.Row([ft.Column([], width=400), self.save, ft.Column([], width=600),
                               self.save2])]))

        self.page.overlay.append(self.bs)

        self.page.update()

    def pick_files_result(self, event: ft.FilePickerResultEvent):
        if event.files:
            selected_file = event.files[0]
            try:
                with open(selected_file.path, "rb") as file:
                    file_data = file.read()
                    self.file_data = file_data  # Store the binary data of the file

                self.file_extension = selected_file.path.split('.')[-1]

                if self.file_extension in ['jpg', 'png', 'jpeg']:
                    self.image_container.image_src_base64 = base64.b64encode(file_data).decode()
                    self.page.update()
                    logging.info(f"Image uploaded: {selected_file.name}")

                elif self.file_extension in ['mp4', 'mov', 'avi']:
                    self.page.update()
                    logging.info(f"Video uploaded: {selected_file.name}")
                else:
                    logging.error(f"Unsupported file format: {self.file_extension}")
            except Exception as e:
                logging.error(f"Error reading file: {e}")
        else:
            logging.info("No files selected or cancelled.")

    def saved(self, event: ft.ControlEvent):
        logging.info(f"Slider rating value: {self.rating.value}")
        if self.file_data:
            data = {
                "title": self.title.value,
                "category_names": list(set(self.category_names.value.split(','))),
                "description": self.description.value,
                "rating": int(self.rating.value),
                "date": str(datetime.today().date()),
                "public": self.public.value
            }
            try:
                # Create an UploadFile object from the file data
                file_ = io.BytesIO(self.file_data)
                upload_file = UploadFile(file=file_, filename=f"video.{self.file_extension}")
                if self.file_extension in ['jpg', 'png', 'jpeg']:
                    data["image"] = base64.b64encode(self.file_data).decode()
                    response, response_j = self.client.add_work(data)
                    logging.info(f"Response: {response}")
                    self.show_bs(response_j["response"])

                elif self.file_extension in ['mp4', 'mov', 'avi']:
                    # Pass the UploadFile object instead of file_data
                    response, response_j = self.client.add_work_video(data, self.file_data, self.file_extension)
                    logging.info(f"Response: {response}")
                    self.show_bs(response_j["response"])
                else:
                    self.show_bs("file format isn't supported")


            except Exception as e:
                logging.error(f"Error during save: {e}")
                self.show_bs("Error during save.")
        else:
            logging.info("No file selected.")
            self.show_bs("No file selected.")

    def saved2(self, event: ft.ControlEvent):
        data = {
            "name": self.name.value,
            "associated_works": [],
            "description": self.category_description.value,
        }
        response, response_j = self.client.add_category(data)
        self.show_bs(response_j["response"])

    def show_bs(self, response):
        self.bs.open = True
        self.sheet_content.value = response
        self.page.update()
        self.bs.update()

    def close_bs(self, e):
        self.bs.open = False
        self.bs.update()

    def submit_search(self, e: ft.ControlEvent):
        # text = f"{e.data}"
        # print("here")
        # print("handle submit:", text)
        # print(f"closing view from {text}")
        # if self.category_names.value == "":
        #     self.category_names.value = text
        # else:
        #     self.category_names.value = self.category_names.value, ", ", text
        # self.page.update()
        pass


    def click_search(self, e: ft.ControlEvent):
        text = f"{e.control.data}"
        print("handle click:", text)
        print(f"closing view from {text}")
        if self.category_names.value == "":
            self.category_names.value = text
        else:
            self.category_names.value = self.category_names.value + "," + text
        self.category_names2.close_view(text)
        self.page.update()
