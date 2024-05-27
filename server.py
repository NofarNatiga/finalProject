# main.py
from time import sleep
import uvicorn

from server_folder.api2 import app

if __name__ == "__main__":
    host = "10.0.0.22"
    uvicorn.run(app, host=host, port=7777)

