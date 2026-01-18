from pydantic import BaseModel, Field
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
    sequence: int | None = None 
    data: TableData | CodeToolData | ParagraphData | HeaderData | QuoteData | ListData

class EditorJSSessionData(BaseModel):
    time: int
    blocks: List[Block]
    version: str
    logged_in_session_id: str
    browser_session_id: str
    article_id: str

class HeadBlock(BaseModel):
    id: str 
    type: str
    data: HeaderData

class ArticleHead(BaseModel):
    time: int
    blocks: List[HeadBlock]
    version: str
    article_id: str

class TitleHeaderDataPub(BaseModel):
    text: str 
    level: int = Field(default=1, frozen=True)

class SubtitleHeaderDataPub(BaseModel):
    text: str 
    level: int = Field(default=3, frozen=True)

class TitleBlockPub(BaseModel):
    type: str = Field(default="title", frozen=True)
    data: TitleHeaderDataPub

class SubtitleBlockPub(BaseModel):
    type: str = Field(default="subtitle", frozen=True)
    data: SubtitleHeaderDataPub

class ArticleHeadPublic(BaseModel):
    blocks: tuple[TitleBlockPub, SubtitleBlockPub] = None