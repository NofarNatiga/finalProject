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
            on_change=self.handle_options,
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
            on_submit=self.handle_submit
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

        self.page.add(self.empty_space, self.for_search, self.empty_space, self.bs)

    def close_bs(self, e):
        self.bs.open = False
        self.bs.update()

    def handle_options(self, e: ft.ControlEvent):
        if self.search_in.value is NoneType:
            response, response_j = self.client.get_all(self.options.value)
        elif self.search_in.value.lower() == "private":
            response, response_j = self.client.get_all(self.options.value)
            print("in private")
        else:
            response, response_j = self.client.get_all_public(self.options.value)

        print(response_j["response"])
        if response_j["response"].lower() == "success":

            self.list1 = response_j["data"]
            self.list1 = list(set(self.list1))
            self.anchor.controls = [
                ft.ListTile(title=ft.Text(f" {i}"), on_click=self.close_anchor, data=i, )
                for i in self.list1
            ]
            self.page.update()
        else:
            print(response_j["response"])

    def close_anchor(self, e):
        text = f"{e.control.data}"
        print(text)
        print(f"closing view from {text}")

        if self.search_in.value.lower() == "public":
            public = True
        else:
            public = False

        what = {"attribute": self.options.value, "name": text, "public": public}
        if public is False:
            response, j_response = self.client.get_images(what)
        else:
            response, j_response = self.client.get_images_public(what)

        if j_response["response"].lower() == "success":
            self.image_data_info_list = j_response["data"]
        else:
            print(j_response)

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

        if self.search_in.value.lower() == "public":
            public = True
        else:
            public = False

        what = {"attribute": self.options.value, "name": text, "public": public}
        if public is False:
            response, j_response = self.client.get_images(what)
        else:
            response, j_response = self.client.get_images_public(what)

        if j_response["response"].lower() == "success":
            self.image_data_info_list = j_response["data"]
        else:
            print(j_response)

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
                        ft.Card(
                            content=ft.Image(
                                src_base64=image_info["data"],
                                width=image_info["width"],
                                height=image_info["height"],
                                repeat=ft.ImageRepeat.NO_REPEAT,
                                border_radius=ft.border_radius.all(10),
                                tooltip=image_info["title"],
                            )
                            , width=270, height=270, color=ft.colors.GREY_50, elevation=50,
                        ), on_click=self.clicked(image_info),
                    )
                )
            else:
                images_grid.controls.append(
                    ft.Container(
                        ft.Card(
                            content=ft.Image(
                                src_base64=image_info["data"],
                                width=700,
                                repeat=ft.ImageRepeat.NO_REPEAT,
                                border_radius=ft.border_radius.all(10),
                                tooltip=image_info["title"]
                            )
                            , width=270, height=270, color=ft.colors.GREY_50, elevation=20,
                        ), on_click=self.clicked(image_info)
                    )
                )

        return images_grid

    def clicked(self, image_info):
        def on_click(event):
            # Clear the page
            self.page.remove(self.empty_space, self.for_search, self.grid)

            self.page.vertical_alignment = 'CENTER'
            self.page.horizontal_alignment = 'CENTER'
            if image_info["type"] == "image":
                media = ft.Image(
                    src_base64=image_info["data"],
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                    fit=ft.ImageFit.CONTAIN
                )
            elif image_info["type"] == "video":
                # Create a Video component using the video URL
                video_url, j_video_url = self.client.video(image_info["title"], image_info["name"])
                j_video_url = j_video_url["video_url"]
                sample_media = [

                    ft.VideoMedia(
                        j_video_url,
                        extras={
                            "artist": "Thousand Foot Krutch",
                            "album": "The End Is Where We Begin",
                        },
                        http_headers={
                            "Foo": "Bar",
                            "Accept": "*/*",
                        },
                    ),
                ]
                media = ft.Video(
                    playlist=sample_media,
                    expand=True,
                    playlist_mode=ft.PlaylistMode.LOOP,
                    fill_color=ft.colors.WHITE,
                    aspect_ratio=16 / 9,
                    volume=100,
                    autoplay=False,
                    filter_quality=ft.FilterQuality.HIGH,
                    muted=False,
                    on_loaded=lambda e: print("Video loaded successfully!"),
                    on_enter_fullscreen=lambda e: print("Video entered fullscreen!"),
                    on_exit_fullscreen=lambda e: print("Video exited fullscreen!"),

                )
            else:
                media = ft.Text("Unsupported media type")

            color = ft.colors.WHITE
            title1 = ft.TextField(label="title", value=image_info["title"], bgcolor=color, height=50)
            categories1 = ft.TextField(label="categories", value=image_info["categories"], bgcolor=color, height=50)
            description1 = ft.TextField(label="description", value=image_info["description"], bgcolor=color, height=50)
            rating1 = ft.Slider(min=0, max=100, divisions=100, label="{value}%", value=image_info["rating"], width=200)
            public1 = ft.Switch(label="public", value=image_info["public"], label_position=ft.LabelPosition.LEFT, )

            delete = ft.ElevatedButton(text="delete work", on_click=lambda event: self.delete(image_info))
            update = ft.ElevatedButton(text="update",
                                       on_click=lambda event: self.update(image_info, title1, categories1, description1,
                                                                          rating1, public1))

            if self.client.name == image_info["name"]:

                c = ft.Column([
                    ft.Text(value="Work Details:", size=19),
                    title1,
                    categories1,
                    description1,
                    ft.Text("Work Rating:"),
                    rating1,
                    public1,
                    ft.Row([update, delete], alignment=ft.alignment.center, width=200, spacing=75)
                ], spacing=12)
            else:
                c = ft.Column([
                    ft.TextField(label="title", value=image_info["title"], read_only=True, bgcolor=color,
                                 height=50),
                    ft.TextField(label="categories", value=image_info["categories"], bgcolor=color, height=50,
                                 read_only=True),
                    ft.TextField(label="description", value=image_info["description"], bgcolor=color, height=50,
                                 read_only=True),
                    ft.Text("Work Rating:"),
                    ft.Slider(min=0, max=100, divisions=100, label="{value}%", disabled=True,
                              value=image_info["rating"]),
                    ft.Switch(label="public", value=image_info["public"], label_position=ft.LabelPosition.LEFT, ),

                ])

            self.y = ft.Row([
                ft.Card(
                    content=ft.Container(
                        content=media,
                    ),
                    width=450,
                    height=450,
                    color=ft.colors.WHITE,
                    elevation=20,
                ), ft.Container(
                    c
                )
            ], alignment=ft.alignment.center, width=800
            )
            self.page.add(self.y)
            self.page.update()

        return on_click

    def update(self, image_info, title, categories, description, rating, public):
        dict1 = {}
        self.page.update()
        print(title.value, description.value, public.value)

        if title.value != image_info["title"]:
            dict1["title"] = title.value

        if categories.value != image_info["categories"]:
            dict1["category_names"] = categories.value

        if description.value != image_info["description"]:
            dict1["description"] = description.value

        if rating.value != image_info["rating"]:
            dict1["rating"] = rating.value

        if public.value != image_info["public"]:
            dict1["public"] = public.value

        print(dict1)
        if dict1 != {}:
            response, j_response = self.client.update_work_details(image_info["title"], dict1)
            print(j_response)
            self.show_bs(j_response["response"])

    def show_bs(self, response):
        self.bs.open = True
        self.sheet_content.value = str(response)
        self.page.update()
        self.bs.update()

    def delete(self, image_info):
        print(image_info["title"])
        response, j_response = self.client.delete_work(image_info["title"])
        if j_response["response"] == "work deleted successfully":
            self.page.remove(self.y)
            Works(self.page, self.client)
