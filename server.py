# main.py
from time import sleep
import uvicorn

from server_folder.api import app

if __name__ == "__main__":
    # host = "10.0.0.22"
    uvicorn.run(app, host="0.0.0.0", port=6666)

