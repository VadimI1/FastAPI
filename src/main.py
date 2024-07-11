import io
import logging
import sys

from io import BytesIO
from uuid import uuid4

from minio import Minio
from replit.web import User

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, UploadFile
from fastapi import Form, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi_sqlalchemy import DBSessionMiddleware, db

from starlette import status
from starlette.responses import StreamingResponse, JSONResponse

from .bd.models import Mem as ModelMem
from .bd.models import User as ModelUser
from .bd.schema import Mem as SchemaMem, TokenSchema
from .bd.schema import Id as SchemaId
from .bd.schema import  UserAuth
from .config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from .deps import get_current_user
from .utils import get_hashed_password, verify_password, create_access_token, create_refresh_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info('API is starting up')

app = FastAPI()

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)


client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
found = client.bucket_exists("mem")
if not found:
    client.make_bucket('mem')
    print("Created bucket mem")
else:
    print("Bucket mem already exists")


@app.post("/memes")
async def add_mem(file: UploadFile, text: str = Form(...), user: User = Depends(get_current_user)):
    try:
        if (file.filename.split('.')[1] == 'jpg' or file.filename.split('.')[1] == 'png'):
            binary_image = file.file.read()
            sh = SchemaMem(text=text, photo=binary_image)
            client.put_object("mem", sh.text, data=io.BytesIO(sh.photo), length=len(sh.photo))

            db_book = ModelMem(text=sh.text, photo=sh.photo)
            db.session.add(db_book)
            db.session.commit()
            return {"message": "Photo saved successfully"}
        else:
            return JSONResponse(status_code=400, content={"message": "Photo saved error. Incorrect image format"})
    except:
        return JSONResponse(status_code=400, content={"message": "Photo saved error"})


@app.get("/memes")
async def list_mem():
    try:
        bd_data = db.session.query(ModelMem).all()
        data = {}
        for item in bd_data:
            data[item.id] = item.text

        return JSONResponse(data)
    except:
       return JSONResponse(status_code=400, content={"message": "Incorrect Data"})

@app.get("/memes/{id}")
async def show_mem(id: int, user: User = Depends(get_current_user)):
    try:
        sh = SchemaId(id=id)
        bd_data = db.session.query(ModelMem).filter(ModelMem.id == sh.id).first()
        filtered_image = BytesIO(bd_data.photo)
        headers = {
            "Content": bd_data.text,
        }
        return StreamingResponse(filtered_image, headers=headers, media_type="image/jpeg")
    except AttributeError:
        return JSONResponse(status_code=400, content={"message": "Incorrect Data. This id is not in the database"})
    except:
        return JSONResponse(status_code=400, content={"message": "Incorrect Data. Error id"})



@app.delete("/memes/{id}")
async def delete_mem(id: int, user: User = Depends(get_current_user)):
    try:
        sh = SchemaId(id=id)
        text = db.session.query(ModelMem.text).filter(ModelMem.id == sh.id).first()
        client.remove_object("mem", text.text)
        db.session.query(ModelMem).filter(ModelMem.id == sh.id).delete(synchronize_session=False)
        db.session.commit()
        return {"message": "Photo delete successfully"}
    except:
        return JSONResponse(status_code=400, content={"message": "Incorrect Data. Error id"})


@app.put("/memes/{id}")
async def update_mem(id: int, file: UploadFile, text: str = Form(...), user: User = Depends(get_current_user)):
    try:
        if (file.filename.split('.')[1] == 'jpg' or file.filename.split('.')[1] == 'png'):
            binary_image = file.file.read()
            sh = SchemaMem(text=text, photo=binary_image)
            shid = SchemaId(id=id)
            bd_data = db.session.query(ModelMem).filter(ModelMem.id == shid.id).first()
            client.put_object("mem", sh.text, data=io.BytesIO(sh.photo), length=len(sh.photo))
            client.remove_object("mem", bd_data.text)
            bd_data.text = sh.text
            bd_data.photo = sh.photo
            db.session.add(bd_data)
            db.session.commit()
            return {"message": "Photo update successfully"}
        else:
            return JSONResponse(status_code=400, content={"message": "Photo update error. Incorrect image format"})
    except:
        return JSONResponse(status_code=400, content={"message": "Incorrect Data. Error id"})


@app.get("/docs")
def read_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json")


@app.post('/signup', summary="Create new user")
async def create_user(data: UserAuth):
    user = db.session.query(ModelUser).filter(ModelUser.email == data.email).first()
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = ModelUser(user_id=uuid4(), email=data.email, password = get_hashed_password(data.password))
    db.session.add(user)
    db.session.commit()
    return user


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.session.query(ModelUser).filter(ModelUser.email == form_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }