import base64
import hashlib
import io
import json
import os
import uuid
from pathlib import Path
from typing import Union

from starlette.staticfiles import StaticFiles

from server_folder import j_classes
import cv2
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from PIL import Image
from fastapi import FastAPI, Query, UploadFile, HTTPException, File, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, String, delete, update, JSON, Boolean
from sqlalchemy.orm import sessionmaker
from typing_extensions import TypedDict
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

base_video_url = "http://10.0.0.22:7777/videos"

global base_path
base_path = "C:\\new"

app = FastAPI(docs_url="/")

DATABASE_URL = "sqlite:///./table9.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("name", String, primary_key=True),
    Column("password", String),
    Column("all_user_data", JSON),
    Column("allowed", Boolean, default=True)

)

admin_users = Table(
    "admin_users",
    metadata,
    Column("name", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("super_admin", Boolean, default=False)
)

metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(BaseModel):
    name: str
    password: str


class AdminUser(BaseModel):
    name: str
    password: str
    super_admin: bool


class WorkDict(TypedDict):
    title: str
    category_names: list[str]
    description: str
    rating: int
    image: str
    date: str
    public: bool


class CategoryDict(TypedDict):
    name: str
    associated_works: list[j_classes.Work]
    description: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/authenticate")
def authenticate(user_data: User) -> dict:
    session = Session()
    user = session.query(users).filter_by(name=user_data.name, password=hash_password(user_data.password)).first()

    if user:
        access_token = create_access_token(data={"sub": user_data.name})
        session.close()
        return {
            "response": "user authenticated",
            "access_token": access_token,
            "token_type": "bearer"
        }

    session.close()
    return {"response": "user not authenticated"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return {"response": "Invalid Token"}
    except JWTError:
        return {"response": "Invalid Token"}

    # Query the user by username
    session = Session()
    user = session.query(users).filter_by(name=username).first()
    session.close()

    if not user:
        return {"response": "User not found"}

    return user


@app.post("/signup")
def signup(user_data: User) -> dict:
    session = Session()
    if session.query(users).filter_by(name=user_data.name).first():  # if name already in use
        return {"response": "User already exists"}

    user_data1 = j_classes.User_Data(name=user_data.name, all_works=[], all_categories=[])  # creating user data object
    user_data1 = json.dumps(user_data1.dump())

    session.execute(
        users.insert().values(
            name=user_data.name, password=hash_password(user_data.password), all_user_data=user_data1)
    )

    session.commit()
    session.close()

    access_token = create_access_token(data={"sub": user_data.name})

    return {
        "response": "signup success",
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/signout")
def signout(current_user: User = Depends(get_current_user)) -> dict:
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()

    if not user_row:
        session.close()
        return {"response": "user not authenticated"}
    # not authenticated will be a better response but im not going to change it now

    query = delete(users).where(
        users.c.name == current_user.name and
        users.c.password == hash_password(current_user.password)
    )
    session.execute(query)
    session.commit()
    session.close()
    return {"response": "signout success"}


@app.post("/update_work_details")
def update_work_details(work_title: str, work_details: dict, current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()

    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    response_data = user_data1.update_work_details(work_title, work_details)
    print(user_data1)
    print(work_details)
    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()
    session.close()

    print(response_data["response"])
    return response_data


@app.post("/update_category_details")
def update_category_details(category_title: str, category_details: dict,
                            current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()

    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    user_data1.update_category_details(category_title, category_details)
    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()

    response_data = {"response": "category updated successfully"}
    print(response_data["response"])

    return response_data


@app.post("/add_category")
def add_category(category: CategoryDict, current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    category = j_classes.Category.load(category)
    user_data1.add_category(category)

    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()

    response_data = {"response": "category added successfully"}

    print(response_data["response"])

    return response_data


@app.post("/delete_category")
def delete_category(category_name: str, current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))
    response_data = user_data1.remove_category(category_name)

    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()

    return response_data


@app.post("/delete_work/{work_name}")
def delete_work(work_name: str, current_user: User = Depends(get_current_user)):
    session = Session()

    user_row = session.query(users).filter_by(name=current_user.name).first()

    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    # Try to remove the work
    response_data = user_data1.remove_work(work_name)
    if response_data["response"] == "work deleted successfully":
        user_data1 = json.dumps(user_data1.dump())
        session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))
        session.commit()

    session.close()

    print(response_data["response"])
    return response_data


@app.get("/for_get_all")
def for_get_all(what: str = Query(...), current_user: User = Depends(get_current_user)):
    session = Session()

    user_row = session.query(users).filter_by(name=current_user.name).first()

    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))
    return get_all(user_data1, what)


def get_all(user_data1: j_classes.User_Data, what: str = Query(...)):
    all_works = user_data1.all_works
    all_categories = user_data1.all_categories

    if what.upper() == "TITLE":
        list1 = [w.title for w in all_works]

    elif what.upper() == "CATEGORY":
        list1 = [c.name for c in all_categories]

    elif what.upper() == "DATE":
        list1 = [w.date for w in all_works]

    elif what.upper() == "RATING":
        list1 = [w.rating for w in all_works]
    else:
        return {"response": "attribute not found"}  # 'what' given is not an option

    return {"data": list1, "response": "success"}


@app.get("/get_all_public")
def get_all_public(what: str = Query(...), current_user: User = Depends(get_current_user)):
    session = Session()
    # Authenticate the user
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    try:
        user_rows = session.query(users).all()

        final_works_list = []
        all_all_categories = []
        categories = []

        for user_row in user_rows:
            user_data_instance = j_classes.User_Data.load(json.loads(user_row.all_user_data))

            filtered_works = [work for work in user_data_instance.all_works if work.public]
            final_works_list.extend(filtered_works)
            for category in user_data_instance.all_categories:
                for w in category.associated_works:
                    if w.public:
                        categories.append(category)
                        break

            all_all_categories.extend(user_data_instance.all_categories)
        user_data_instance = j_classes.User_Data(current_user.name, final_works_list, all_all_categories)
        return get_all(user_data_instance, what)
    finally:
        session.close()


@app.get("/for_get_images")
def for_get_images(attribute, name, public=False, current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))
    response = get_images(attribute, name, user_data1, public)
    session.close()
    return response


def get_images(attribute, value, user_data1: j_classes.User_Data, public: bool):
    all_works = user_data1.all_works
    all_categories = user_data1.all_categories

    if attribute.lower() == "all":
        image_data_and_info = get_image_info_list(all_works, user_data1.name)

    elif attribute.lower() == "category":
        c = None
        for category in all_categories:
            if category.name == value:
                c = category
                print(c.name)
                break
        if c is None:
            return {"response": "category is empty"}

        list1 = c.associated_works
        if public:
            for work in c.associated_works:
                if work.public:
                    list1.append(work)
        image_data_and_info = get_image_info_list(list1, user_data1.name)

    elif attribute.lower() == "title":
        relevant_works = []
        for work in all_works:
            if work.title == value:
                relevant_works.append(work)

        image_data_and_info = get_image_info_list(relevant_works, user_data1.name)

    elif attribute.lower() == "date":
        relevant_works = []
        for work in all_works:
            if work.date == value:
                relevant_works.append(work)

        image_data_and_info = get_image_info_list(relevant_works, user_data1.name)

    elif attribute.lower() == "rating":
        relevant_works = []
        for work in all_works:
            if work.rating == int(value):
                relevant_works.append(work)

        image_data_and_info = get_image_info_list(relevant_works, user_data1.name)
    else:  # attribute given was not an option somehow
        return {"response": "attribute not found"}

    return {"data": image_data_and_info, "response": "success"}


def get_image_info_list(works, name: str):
    image_info_list = []
    # Iterate over each work in the provided list of works
    for work in works:
        # Check if the file extension indicates an image file
        if Path(work.image_path).suffix in ['.jpg', '.png', '.jpeg']:
            # Open the image file in binary mode
            with open(work.image_path, "rb") as image:
                image_data = image.read()
                # Construct the path to the key file
                path = base_path + "\\" + name + "\\key.key"

                with open(path, 'rb') as f:
                    key = f.read()

                fernet = Fernet(key)
                # Decrypt the image data using the Fernet cipher
                image_data = fernet.decrypt(image_data)
                # Open the decrypted image using PIL
                image = Image.open(
                    io.BytesIO(image_data))  # loads the image data from bytes format into a PIL Image object
                width, height = image.size
                image_info = {"data": base64.b64encode(image_data).decode(),
                              "type": "image",
                              "width": width,
                              "height": height,
                              "title": work.title,
                              "description": work.description,
                              "categories": work.category_names,
                              "rating": work.rating,
                              "public": work.public,
                              "name": name

                              }
                image_info_list.append(image_info)

        elif Path(work.image_path).suffix in ['.mp4', '.mov', '.avi']:
            print("inside video")
            # Extract a preview image from the video file
            preview_image_data = extract_preview_image(work.image_path, )
            # Construct a dictionary containing video information
            image_info = {
                "type": "video",
                "data": base64.b64encode(preview_image_data).decode(),
                "title": work.title,
                "description": work.description,
                "categories": work.category_names,
                "rating": work.rating,
                "public": work.public,
                "name": name

            }
            image_info_list.append(image_info)
        else:
            pass
    # Return the list of image information dictionaries
    return image_info_list


@app.get("/public_works")
def public_works(attribute, name, current_user: User = Depends(get_current_user)):
    # Create a session
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}
    try:
        user_rows = session.query(users).all()

        final_info_list = []

        for user_row in user_rows:
            user_data_instance = j_classes.User_Data.load(json.loads(user_row.all_user_data))

            filtered_works = [work for work in user_data_instance.all_works if work.public]

            user_data_instance.all_works = filtered_works
            info_list = get_images(attribute, name, user_data_instance, True)
            if info_list["response"] == "success":
                data_list = info_list["data"]
                final_info_list.extend(data_list)
            else:
                return info_list
        return {"data": final_info_list, "response": "success"}

    finally:
        session.close()


def extract_preview_image(video_path):
    vcap = cv2.VideoCapture(video_path)

    video_width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    vcap = cv2.VideoCapture(video_path)
    res, im_ar = vcap.read()
    im_ar = cv2.resize(im_ar, (video_width, video_height), 0, 0, cv2.INTER_LINEAR)
    res, thumb_buf = cv2.imencode('.png', im_ar)
    bt = thumb_buf.tostring()
    return bt


@app.post("/add_work")
def add_work(work: WorkDict, current_user: User = Depends(get_current_user)):
    session = Session()

    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    if not is_valid_base64_image_magic_number(work["image"]):
        session.close()
        return {"response": "Invalid image data"}

    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row.allowed:
        session.close()
        return {"response": "user used all free storage"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    image_data = base64.b64decode(work["image"])

    image_path = upload_image(image_data, current_user)

    work_dict = {
        "title": work["title"],
        "category_names": work["category_names"],
        "description": work["description"],
        "rating": work["rating"],
        "image_path": image_path,  # saving the path
        "date": work["date"],
        "public": work["public"]
    }

    work = j_classes.Work.load(work_dict)

    print(type(user_data1))
    user_data1.add_work(work)
    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()
    session.close()

    response_data = {"response": "work added successfully"}

    print(response_data["response"])

    print(response_data)

    return response_data


def upload_image(image_data: bytes, current_user: User) -> str:
    global base_path

    path = base_path + "\\" + current_user.name + "\\" + "image"
    if not os.path.exists(path):
        os.makedirs(path)
        os.system(f'attrib +h "{path}"')  # hiding the folder cause riki said so

    key_path = base_path + "\\" + current_user.name + "\\" + 'key.key'
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        # os.makedirs(key_path)
        with open(key_path, 'wb') as f:
            f.write(key)

    else:
        with open(key_path, 'rb') as f:
            key = f.read()

    fernet = Fernet(key)
    locked_photo = fernet.encrypt(image_data)

    filename = uuid.uuid4().hex + ".jpg"

    file_path = Path(path) / filename

    with open(file_path, "wb") as f:
        f.write(locked_photo)

    return str(file_path)


def is_valid_base64_image_magic_number(base64_data: str) -> bool:
    # Check if base64 data starts with a valid image prefix (JPEG, PNG, GIF, BMP)
    valid_prefixes = [
        "data:image/jpeg;base64,",  # JPEG images
        "data:image/png;base64,",  # PNG images
        "data:image/gif;base64,",  # GIF images
        "data:image/bmp;base64,"  # BMP images
    ]
    flag = True
    for a in valid_prefixes:
        if a not in base64_data:
            flag = False
    if flag is True:
        return flag

    # Remove the prefix from the base64 data
    base64_data = base64_data.split(",")[1] if "," in base64_data else base64_data

    try:
        # Decode the base64 data
        decoded_data = base64.b64decode(base64_data)

        # Check the magic number
        magic_numbers = {
            'jpeg': b'\xff\xd8\xff',  # JPEG magic number
            'png': b'\x89PNG\r\n\x1a\n',  # PNG magic number
            'gif': b'GIF',  # GIF magic number
            'bmp': b'BM'  # BMP magic number
        }

        for file_type, magic_number in magic_numbers.items():
            if decoded_data.startswith(magic_number):
                return True

        return False
    except Exception:
        return False


@app.post("/add_work_video")
def add_work_video2(title: str, category_names: list[str], rating: int, description: str, public: bool, date: str,
                    video_file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    session = Session()
    user_row = session.query(users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    if not user_row.allowed:
        session.close()
        return {"response": "user used all free storage"}

    user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))

    # Save the video file and get the file path
    video_path = save_video_file(video_file, current_user)

    # Prepare work data dictionary
    work_dict = {
        "title": title,
        "category_names": category_names,
        "description": description,
        "rating": rating,
        "image_path": video_path,  # Save the video path
        "date": date,
        "public": public
    }
    print("Video Path:", video_path)

    # Create a Work instance (assuming you have a Work class)
    work_instance = j_classes.Work.load(work_dict)

    # Add work to user data and update user data in the database
    user_data1.add_work(work_instance)
    user_data1 = json.dumps(user_data1.dump())

    session.execute(update(users).where(users.c.name == current_user.name).values(all_user_data=user_data1))

    session.commit()
    session.close()

    return {"response": "Work with video added successfully"}


# Function to save the video file
def save_video_file(video_file: UploadFile, current_user: User) -> str:
    # Define the base directory for storing user videos
    global base_path
    print("inside the save in the server")

    # Create a directory for the current user if it does not exist
    user_directory = os.path.join(base_path, current_user.name, "video")

    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
        os.system(f'attrib +h "{user_directory}"')

    mount_path = f"/videos/{current_user.name}"
    app.mount(mount_path, StaticFiles(directory=user_directory), name=current_user.name)

    # Get the file extension from the uploaded video file
    original_extension = video_file.content_type
    print("original extension", original_extension)

    # Generate a unique filename using a UUID and the original file extension
    print(original_extension)
    filename = uuid.uuid4().hex + "." + original_extension
    print(filename)
    # Define the full file path for the new video file
    file_path = Path(user_directory) / filename

    # Save the video file to the file path
    with open(file_path, "wb") as f:
        chunk = video_file.file.read(1024)
        while chunk:
            f.write(chunk)
            chunk = video_file.file.read(1024)

    return str(file_path)


@app.get("/video_url/{name}/{title}")
def get_video_url(name: str, title:str, current_user: User = Depends(get_current_user)):
    print("inside video url!!!")
    session = Session()
    if name != current_user.name:
        user_row = session.query(users).filter_by(name=name).first()
        if user_row is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_data1 = j_classes.User_Data.load(json.loads(user_row.all_user_data))
        all_works = user_data1.all_works
        for a in all_works:
            if a.title == title:
                if not a.public:
                    session.close()
                    return {"response": "user not authenticated"}
                else:
                    video_path = a.image_path
                    if video_path is None:
                        raise HTTPException(status_code=404, detail="Video title not found")

                    video_file = Path(video_path)
                    if not video_file.exists() or not video_file.is_file():
                        raise HTTPException(status_code=404, detail="Video file not found")

                    # Construct the video URL
                    video_url = f"{base_video_url}/{name}/{video_file.name}"
                    session.close()
                    return {"response": "success", "video_url": video_url}

    try:
        # Fetch user data
        user_row = session.query(users).filter_by(name=current_user.name).first()
        if user_row is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Load user data
        user_data = j_classes.User_Data.load(json.loads(user_row.all_user_data))

        # Find the video path based on the title
        video_path = None
        for work in user_data.all_works:
            if work.title == title:
                video_path = work.image_path
                break

        if video_path is None:
            raise HTTPException(status_code=404, detail="Video title not found")

        # Verify the video file exists
        video_file = Path(video_path)
        if not video_file.exists() or not video_file.is_file():
            raise HTTPException(status_code=404, detail="Video file not found")

        # Construct the video URL
        video_url = f"{base_video_url}/{current_user.name}/{video_file.name}"

        # Return the video URL
        return {"response": "success", "video_url": video_url}

    finally:
        session.close()


def get_folder_size(name_of_user):
    size = 0
    global base_path
    Folder_path = base_path + "//" + name_of_user

    # get size
    for path, dirs, files in os.walk(Folder_path):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    # display size

    return {"text": "Folder size: " + str(size / 1048576) + "MB", "data": size / 1048576}


def get_user_data() -> dict[str, Union[str, list[j_classes.User_Data]]]:
    session = Session()
    try:
        user_rows = session.query(users).all()

        final_info_list = []

        for user_row in user_rows:
            user_data_instance = j_classes.User_Data.load(json.loads(user_row.all_user_data))
            final_info_list.append(user_data_instance)

        return {"data": final_info_list, "response": "success"}

    except Exception as e:
        # Log other unexpected errors
        print(f"Unexpected error: {e}")
        # Return an appropriate response to the client
        return {"response": "error", "data": "An unexpected error occurred."}
    finally:
        # Ensure the session is closed
        session.close()


def get_current_user_admin(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return {"response": "Invalid Token"}
    except JWTError:
        return {"response": "Invalid Token"}

    # Query the user by username
    session = Session()
    user = session.query(admin_users).filter_by(name=username).first()
    session.close()

    if not user:
        return {"response": "User not found"}

    return user


@app.get("/for_gui")
def for_gui(current_user: AdminUser = Depends(get_current_user_admin)):
    session = Session()
    user_row = session.query(admin_users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}
    session.close()

    users_data = []
    name_and_space = []

    all_users_data = get_user_data()
    if all_users_data["response"] == "success":
        users_data = all_users_data["data"]
        for user_data in users_data:
            name_and_space.append({"name": user_data.name, "size": get_folder_size(user_data.name)})
        return {"response": "success", "data": name_and_space}
    else:
        return all_users_data


@app.post("/add_admin")
def add_admin(new_user: AdminUser, current_user: AdminUser = Depends(get_current_user_admin)):
    session = Session()
    user = session.query(admin_users).filter_by(name=current_user.name,
                                                password=hash_password(current_user.password)).first()

    if session.query(admin_users).filter_by(name=new_user.name).first():  # if name already in use
        session.close()
        return {"response": "User already exists"}

    if user and user.super_admin:
        session.execute(
            admin_users.insert().values(
                name=new_user.name, password=hash_password(current_user.password), super_admin=new_user.super_admin
            )
        )
        session.commit()
        session.close()

        return {"response": "admin added successfully"}
    return {"response": "user isn't authorize"}


@app.post("/authenticate_admin")
def authenticate_admin(current_user: AdminUser):
    session = Session()

    user = session.query(admin_users).filter_by(name=current_user.name, password=hash_password(current_user.password),
                                                super_admin=current_user.super_admin).first()
    if user:
        access_token = create_access_token(data={"sub": current_user.name})
        session.close()
        return {
            "response": "user authenticated",
            "access_token": access_token,
            "token_type": "bearer"
        }

    session.close()
    return {"response": "user not authenticated"}


@app.post("/block")
def block_from_adding(user: str, current_user: AdminUser = Depends(get_current_user_admin)):
    session = Session()
    user_row = session.query(admin_users).filter_by(name=current_user.name).first()
    if not user_row:
        session.close()
        return {"response": "user not authenticated"}

    session.execute(update(users).where(users.c.name == user).values(allowed=False))
    session.commit()
    session.close()
    return {"response": "user block success"}


@app.get("/share_with")
def share_with():
    pass
