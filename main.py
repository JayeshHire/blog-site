from fastapi import FastAPI, Body, Depends, Request, Form, HTTPException, status, Cookie
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
from dependencies.session_depends import user_login, user_logout, user_signup, init_editor_session, store_article_data, load_article_head_data, load_article_body_data
from user_basemodel import SigninBaseModel, SignupBaseModel
from model.user_model import UserCreate, UserPublic, User
from passlib.context import CryptContext
from sqlmodel import or_
from sqlalchemy.exc import NoResultFound, IntegrityError
from model.tool_model import Article
from uuid import UUID
from TelemetryConfig.telemetry_config import tracer, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


@asynccontextmanager
async def lifespan( app: FastAPI):
    init_db_setup()
    yield

app = FastAPI(lifespan=lifespan)

FastAPIInstrumentor.instrument_app(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/dist", StaticFiles(directory="dist"), name="bundle")

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
    user = request.session.get("user_id")
    if user is None:
        return {"username": None, "message": "User not logged in"}
    return {"user": user}

@app.get("/", response_class=HTMLResponse)
async def get_index(initialized: Annotated[bool, Depends(init_editor_session)]):
    if initialized:
        with open("./static/html/main.html", 'r') as f:
            content = f.read()
        return content
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to initialize the application."
                            )
    
'''
When a new caller calls the domain.
Main index page is returned which consists
of the editor and few user options.
An editor session is created and a new article
associated with that editor is created.

OnChange of title and subtitle, article objects
title and subtitle is updated.

If the user logs in then the article in the editor
is associated with that user.

OnChange of data in the article body. That data is
updated in the db.
'''

@app.post("/editorjs/save/article/body")
async def create_data(editorjsdata: Annotated[ bool, Depends(store_editorjs_data)]):
    if editorjsdata:
        return "SUCCESS"
    return "FAILURE"

@app.get("/article/id")
async def get_current_article_id(request: Request):
    article_id = request.session.get("article_id")
    return {"article_id": article_id}

@app.post("/editorjs/save/article/head")
async def save_article_head(article: Annotated[Article | None, Depends(store_article_data)]):
    print(article)
    if article: 
        return "SUCCESS" 
    return "FAILURE"
    

@app.get("/user/has_logged_in")
async def has_logged_in(request: Request):
    u_id = request.session.get("user_id")
    if u_id:
        return {
            "type": "status",
            "entity": "user",
            "data": {
                "has_logged_in": True
            }
        }
    return  {
            "type": "status",
            "entity": "user",
            "data": {
                "has_logged_in": False
            }
        }

# methods for populating the earlier states 
# of the browser window
@app.get("/load/article/head/previous_state")
async def load_article_head(article_head_pub: Annotated[ArticleHeadPublic | None, Depends(load_article_head_data)]
                            ) -> ArticleHeadPublic:
    return article_head_pub


@app.get("/load/article/body/previous_state")
async def load_article_body(article_body_pub: Annotated[EditorJSSessionDataPub | None, Depends(load_article_body_data)]
                            ) -> EditorJSSessionDataPub:
    return article_body_pub


""" 
This returns the login status of the user.
It tells the frontend application whether the user has logged in 
or not.
"""
@app.get("/user/status/is_logged_in")
async def is_user_logged_in(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        return {"is_logged_in": True}
    else:
        return {"is_logged_in": False}
    

""" 
These route handlers are for sending all the 
markups directly to the frontend where the 
frontend will populate these markups in other
elements.
"""
@app.get("/markup/form/signin")
def get_form_signin():
    signin_form = ""
    with open("./static/html/chunks/form_signin.html", 'r') as f:
        signin_form += f.read() 
    return {
        "signin_form": signin_form
    }

@app.get("/markup/form/signup")
def get_form_signin():
    signup_form = ""
    with open("./static/html/chunks/form_signup.html", 'r') as f:
        signup_form += f.read() 
    return {
        "signup_form": signup_form
    }

@app.get("/markup/form/logout")
def get_form_signin():
    logout_form = ""
    with open("./static/html/chunks/form_logout.html", 'r') as f:
        logout_form += f.read() 
    return {
        "logout_form": logout_form
    }

@app.get("/dev/clear_session")
def clear_session(request: Request, browser_id: Annotated[UUID | None, Cookie()]):
    user_id = request.session.get("user_id")
    # browser_id = request.session.get("browser_id")
    # request.session.clear()
    return {
        "user_id": user_id,
        "browser_id": browser_id
    }