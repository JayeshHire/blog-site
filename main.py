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
from dependencies.session_depends import user_login, user_logout, user_signup
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
                user: Annotated[UserPublic, Depends(user_signup)]
                ) -> UserPublic | dict:
    return user

@app.post("/signin")
async def signin(request: Request, 
                user: Annotated[UserPublic, Depends(user_login)]
                ):
    return user


@app.get("/logout")
async def logout(request: Request,
                 is_logged_out: Annotated[bool, Depends(user_logout)]
                 ):
    if is_logged_out:
        return {"message": "logged out"}
    return {"message": "user is not logged out yet."}


@app.get("/current_user") 
async def get_curr_user(request: Request):
    return {
        'user_id': request.session.get("user_id"),
        'username': request.session.get("username"),
        'email': request.session.get("email"),
        'editor_session_id': request.session.get('editor_session_id'),
        'browser_id': request.session.get('browser_id')
    }


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