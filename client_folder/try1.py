import requests
import json
from fastapi import UploadFile


class Client:
    def __init__(self, url):
        self.name = None
        self.password = None
        self.token = None  # Add a token attribute to store the JWT token
        self.server_address = url

    def authenticate(self, name, password):
        credentials = {"name": name, "password": password}
        response_ = requests.post(
            f"{self.server_address}/authenticate",
            json=credentials
        )

        response_json = response_.json()
        print(response_, response_json)

        if response_json["response"].upper() == "USER AUTHENTICATED":
            self.name = name
            self.password = password
            self.token = response_json.get("access_token")  # Store the token

        return response_, response_json

    def signout(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response_ = requests.post(
            f"{self.server_address}/signout",
            headers=headers
        )
        return response_, response_.json()

    def add_work(self, work_data: dict):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data_ = {"work": work_data}
        response_ = requests.post(
            f"{self.server_address}/add_work",
            json=data_,
            headers=headers
        )
        return response_, response_.json()

    def add_work_video(self, work_data: dict, video_binary_data: bytes, file_type: str):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.server_address}/add_work_video"
        files_ = {
            "video_file": (f"video.{file_type}", video_binary_data, file_type)
        }
        form_data = {
            "title": work_data["title"],
            "category_names": work_data["category_names"],
            "rating": work_data["rating"],
            "description": work_data["description"],
            "public": work_data["public"],
            "date": work_data["date"]
        }

        response_ = requests.post(
            url,
            params=form_data,
            files=files_,
            headers=headers
        )
        return response_, response_.json()

    def add_category(self, category_data: dict):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data_ = {"category": category_data}
        response_ = requests.post(
            f"{self.server_address}/add_category",
            json=data_,
            headers=headers
        )
        return response_, response_.json()

    def signup(self, name, password):
        credentials = {"name": name, "password": password}
        response_ = requests.post(
            f"{self.server_address}/signup",
            json=credentials
        )

        response_json = response_.json()
        print(response_json)

        if response_json["response"].upper() == "SIGNUP SUCCESS":
            self.name = name
            self.password = password

        return response_, response_json

    def get_all(self, what: str):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.server_address}/for_get_all"
        params = {"what": what}
        response_ = requests.get(url, params=params, headers=headers)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_all_public(self, what: str):
        url = f"{self.server_address}/get_all_public"
        params = {"what": what}
        response_ = requests.get(url, params=params)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_images(self, value: dict):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.server_address}/for_get_images"
        params = value
        response_ = requests.get(url, params=params, headers=headers)

        return response_, response_.json()

    def get_images_public(self, value: dict):
        url = f"{self.server_address}/public_works"
        params = value
        response_ = requests.get(url, params=params)

        return response_, response_.json()

    def update_work_details(self, work_title: str, work_details: dict):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data_ = {"work_details": work_details}
        response_ = requests.post(
            f"{self.server_address}/update_work_details",
            json=data_,
            params={"work_title": work_title},
            headers=headers
        )
        return response_, response_.json()

    def delete_work(self, work_name):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response_ = requests.post(
            f"{self.server_address}/delete_work/{work_name}",
            headers=headers
        )
        return response_, response_.json()

    def video(self, title):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response_ = requests.get(
            f"{self.server_address}/video_url/{title}",
            headers=headers
        )

        if response_.status_code == 200:
            return response_, response_.json()
        else:
            # Handle non-successful responses (e.g., 401, 404, etc.)
            print(f"Failed to fetch video: HTTP {response_.status_code} - {response_.text}")
            response_.raise_for_status()  # Raise an HTTPError for non-successful responses
