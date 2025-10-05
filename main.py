from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel
from typing import Any, Optional, List, Annotated

app = FastAPI()

app.mount("/static", StaticFiles(directory="dist"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("./index.html", 'r') as f:
        content = f.read()
    return content


import datetime
from zoneinfo import ZoneInfo

def convert_to_IST(unix_timestamp: int) -> datetime.datetime:
    unix_timestamp = unix_timestamp / 1000 # convert from ms to sec
    utc = datetime.datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc)
    ist = utc.astimezone(ZoneInfo("Asia/Kolkata"))
    return ist 


class TableData(BaseModel):
    content: List[List[str]]

class CodeToolData(BaseModel):
    code: str
    languageCode: str

class ParagraphData(BaseModel):
    text: str

class HeaderData(BaseModel):
    text: str
    level: int

class QuoteData(BaseModel):
    text: str
    caption: str
    alignment: str

class ListItem(BaseModel):
    content: str
    meta: str | None
    items: Optional[List["ListItem"]] = None

class ListData(BaseModel):
    style: str
    meta: str | None
    items: Optional[List["ListItem"]] = None

class Block(BaseModel):
    id: str
    type: str
    data: TableData | CodeToolData | ParagraphData | HeaderData | QuoteData | ListData

class EditorJSSessionData(BaseModel):
    time: int
    blocks: List[Block]
    version: str
    logged_in_session_id: str
    browser_session_id: str


@app.post("/editorjs")
async def create_data(item: Annotated[EditorJSSessionData, Body()]):
    # data = json.loads(item))
    # print(json.dumps(item, indent=3))
    print(type(item))
    return item

