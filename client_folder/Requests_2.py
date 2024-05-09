import requests
import json
from fastapi import UploadFile


class Client:
    def __init__(self, url):
        self.name = None
        self.password = None
        self.server_address = url

    def authenticate(self, name, password):
        credentials = {"name": name, "password": password}
        response_ = requests.post(
            f"{self.server_address}/authenticate",
            json=credentials
        )
        print(response_, response_.json())

        if response_.json()["response"].upper() == "USER AUTHENTICATED":
            self.name = name
            self.password = password

        return response_, response_.json()

    def signout(self):
        credentials = {"name": self.name, "password": self.password}
        response_ = requests.post(
            f"{self.server_address}/signout",
            json=credentials
        )
        return response_, response_.json()

    def add_work(self, work_data: dict):
        data_ = {"current_user": {"name": self.name, "password": self.password}, "work": work_data}
        response_ = requests.post(
            f"{self.server_address}/add_work",
            json=data_
        )
        return response_, response_.json()

    def add_work_video(self, work_data: dict, video_binary_data: bytes, type: str):
        url = f"{self.server_address}/add_work_video"

        files_ = {
            "video_file": (f"video.{type}", video_binary_data, type)
        }
        form_data = {
            "title": work_data["title"],
            "category_names": work_data["category_names"],
            "rating": work_data["rating"],
            "description": work_data["description"],
            "public": work_data["public"],
            "date": work_data["date"],
            "password": self.password,
            "name": self.name
        }

        response_ = requests.post(
            url,
            params=form_data,
            files=files_
        )
        return response_, response_.json()

    def add_category(self, category_data: dict):
        data_ = {"current_user": {"name": self.name, "password": self.password}, "category": category_data}
        response_ = requests.post(
            f"{self.server_address}/add_category",
            json=data_
        )
        return response_, response_.json()

    def signup(self, name, password):
        credentials = {"name": name, "password": password}
        response_ = requests.post(
            f"{self.server_address}/signup",
            json=credentials
        )
        print(response_.json())
        if response_.json()["response"].upper() == "SIGNUP SUCCESS":
            self.name = name
            self.password = password

        print(response_)
        return response_, response_.json()

    def get_all(self, what: str):
        credentials = {"name": self.name, "password": self.password}
        url = f"{self.server_address}/for_get_all"
        params = {"what": what}
        response_ = requests.get(url, params=params, json=credentials)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_all_public(self, what: str):
        credentials = {"name": self.name, "password": self.password}
        url = f"{self.server_address}/get_all_public"
        params = {"what": what}
        response_ = requests.get(url, params=params, json=credentials)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_images(self, value: dict):
        credentials = {"name": self.name, "password": self.password}
        url = f"{self.server_address}/for_get_images"
        params = value
        response_ = requests.get(url, params=params, json=credentials)

        return response_, response_.json()

    def get_images_public(self, value: dict):
        credentials = {"name": self.name, "password": self.password}
        url = f"{self.server_address}/public_works"
        params = value
        response_ = requests.get(url, params=params, json=credentials)

        return response_, response_.json()

    def update_work_details(self, work_title: str, work_details: dict):
        data_ = {"current_user": {"name": self.name, "password": self.password}, "work_details": work_details}
        response_ = requests.post(
            f"{self.server_address}/update_work_details",
            json=data_,
            params={"work_title": work_title}
        )
        return response_, response_.json()

    def delete_work(self, work_name):
        response_ = requests.post(
            f"{self.server_address}/delete_work/{self.name}/{self.password}/{work_name}",
        )
        return response_, response_.json()

    def video(self, title):
        response_ = requests.get(
            f"{self.server_address}/video_url/{self.name}/{self.password}/{title}",
        )
        if response_.status_code == 200:
            return response_, response_.json()
        else:
            # Handle non-successful responses (e.g., 401, 404, etc.)
            print(f"Failed to fetch video: HTTP {response_.status_code} - {response_.text}")
            response_.raise_for_status()  # Raise an HTTPError for non-successful responses

