import requests
import json
from fastapi import UploadFile


class Client:
    def __init__(self, url):
        self.token_type = None
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

        if response_.status_code == 200:
            data = response_.json()
            self.token = access_token = data.get("access_token")
            self.token_type = data.get("token_type")
            print("Authentication successful")
            print("Access Token:", access_token)
            if response_.json()["response"] == "user authenticated":
                self.name = name
                self.password = password
            return response_, response_.json()
        else:
            print("Authentication failed")

    def signout(self):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        response_ = requests.post(
            f"{self.server_address}/signout",
            headers=headers
        )
        return response_, response_.json()

    def add_work_video(self, work_data: dict, video_binary_data: bytes, file_type: str):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
        }

        url = f"{self.server_address}/add_work_video"
        files_ = {
            "video_file": (f"video.{file_type}", video_binary_data, file_type)
        }
        form_data = {
            "title": work_data["title"],
            "rating": work_data["rating"],
            "description": work_data["description"],
            "public": work_data["public"],
            "date": work_data["date"],
        }

        response_ = requests.post(
            url,
            params=form_data,
            json={"category_names": work_data["category_names"]},
            files=files_,
            headers=headers
        )

        print(response_, response_.json())
        return response_, response_.json()

    def add_category(self, category_data: dict):
        # Define the headers with the authorization token
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }

        # Make the POST request with the category data as the request body
        response_ = requests.post(
            f"{self.server_address}/add_category",
            json=category_data,
            headers=headers  # Include headers for authentication
        )

        print(response_, response_.json())
        return response_, response_.json()

    def add_work(self, work_data: dict):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        response_ = requests.post(
            f"{self.server_address}/add_work",
            json=work_data,
            headers=headers
        )
        return response_, response_.json()

    def update_work_details(self, work_title: str, work_details: dict):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        response_ = requests.post(
            f"{self.server_address}/update_work_details",
            json=work_details,
            params={"work_title": work_title},
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

        data = response_json

        if response_json["response"].upper() == "SIGNUP SUCCESS":
            self.name = name
            self.password = password
            self.token = access_token = data.get("access_token")
            self.token_type = data.get("token_type")

        return response_, response_json

    def get_all(self, what: str):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        url = f"{self.server_address}/for_get_all"
        params = {"what": what}
        response_ = requests.get(url, params=params, headers=headers)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_all_public(self, what: str):
        url = f"{self.server_address}/get_all_public"
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
        }
        params = {"what": what}
        response_ = requests.get(url, params=params, headers=headers)

        print(response_.json())
        print(response_)

        return response_, response_.json()

    def get_images(self, value: dict):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
        }
        url = f"{self.server_address}/for_get_images"
        params = value
        response_ = requests.get(url, params=params, headers=headers)

        return response_, response_.json()

    def get_images_public(self, value: dict):
        url = f"{self.server_address}/public_works"
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
        }
        params = value
        response_ = requests.get(url, params=params, headers=headers)

        return response_, response_.json()

    def delete_work(self, work_name):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        response_ = requests.post(
            f"{self.server_address}/delete_work/{work_name}",
            headers=headers
        )
        return response_, response_.json()

    def video(self, title, name):
        headers = {
            "Authorization": f"{self.token_type} {self.token}",
            "Content-Type": "application/json"
        }
        response_ = requests.get(
            f"{self.server_address}/video_url/{title}/{name}",
            headers=headers,
        )
        print(response_, response_.json())

        if response_.status_code == 200:
            return response_, response_.json()
        else:
            print(f"Failed to fetch video: HTTP {response_.status_code} - {response_.text}")
            response_.raise_for_status()  # Raise an HTTPError for non-successful responses
