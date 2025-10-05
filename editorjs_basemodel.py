from pydantic import BaseModel
from typing import List, Optional

# input and output data model for editorjs plugin
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
    meta: dict = {}
    items: Optional[List["ListItem"]] = None

class ListData(BaseModel):
    style: str
    meta: dict = {}
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