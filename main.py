from fastapi import FastAPI, Body, Depends, Request, Form, HTTPException, status
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel, Json, field_validator, ValidationError
from typing import Any, Optional, List, Annotated
from database import get_session, init_db_setup
from sqlmodel import Session, select
from editorjs_basemodel import *
from dependencies.editorjs_data_store import store_editorjs_data
from user_basemodel import SigninBaseModel, SignupBaseModel
from model.user_model import UserCreate, UserPublic, User
from passlib.context import CryptContext
from sqlmodel import or_
from sqlalchemy.exc import NoResultFound, IntegrityError

@asynccontextmanager
async def lifespan( app: FastAPI):
    init_db_setup()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/bundled-js", StaticFiles(directory="dist"), name="bundle")

app.add_middleware(SessionMiddleware, 
                   secret_key="#234Hdjiru85&8$hd^&!jdkf+=-09*HgY&8^4",
                   https_only=False
                   )

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str :
    hash = pwd_context.hash(password.encode("utf-8"))
    return hash

def verify_password(password: str, hashed_password: str)->bool:
    return pwd_context.verify(password, hashed_password)

@app.post("/signup")
async def signup(request: Request, 
                new_user: Annotated[UserCreate, Form()],
                session: Annotated[Session, Depends(get_session)]
                ) -> UserPublic | dict:
    # encrypt the password before saving
    hashed_password = hash_password(new_user.password)
    try:
        user = User.model_validate(new_user, update={"hashed_password": hashed_password})
        session.add(user)
        session.commit()
        request.session["user"] = UserPublic.model_validate(user)
    except IntegrityError:
        return {"message": "User with this username or email already exists"}
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username should not contain '@' symbol"
        )
    return new_user

@app.post("/signin")
async def signin(request: Request, 
                user: Annotated[SigninBaseModel, Form()],
                session: Annotated[Session, Depends(get_session)]
                ):
    # get existing user
    try:
        existing_user = session.exec(
            select(User)
            .where(or_(User.username == user.username_or_email,
                       User.email == user.username_or_email))
        ).one()
        authorized = verify_password(user.password, existing_user.hashed_password)
        if authorized:
            request.session["user"] = UserPublic.model_validate(existing_user).model_dump()
            return {"message": "logged in successfully"}
        else:
            return {"message": "try again. Your password is incorrect"}
    except NoResultFound:
        return {"message": "No user found"}

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "logged out"}

@app.get("/profile")
async def get_profile(request: Request):
    user = request.session.get("user")
    if user is None:
        return {"username": None, "message": "User not logged in"}
    return {"user": user}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("./static/html/main.html", 'r') as f:
        content = f.read()
    return content

@app.post("/editorjs")
async def create_data(editorjsdata: Annotated[ bool, Depends(store_editorjs_data)]):
    if editorjsdata:
        return "SUCCESS"
    return "FAILURE"