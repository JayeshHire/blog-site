from fastapi import FastAPI, Body, Depends
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel, Json, field_validator
from typing import Any, Optional, List, Annotated
from database import get_session, init_db_setup
from sqlmodel import Session, select
from editorjs_basemodel import *

@asynccontextmanager
async def lifespan( app: FastAPI):
    init_db_setup()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="dist"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("./index.html", 'r') as f:
        content = f.read()
    return content



@app.post("/editorjs")
async def create_data(editorjsdata: Annotated[ bool, Depends(save_editorjs_data)]):
    if editorjsdata:
        return "SUCCESS"
    return "FAILURE"
