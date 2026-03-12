from pydantic import BaseModel, Field,  ConfigDict
from typing import List, Optional

# input and output data model for editorjs plugin
class TableData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: List[List[str]]

class CodeToolData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    languageCode: str

class ParagraphData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str

class HeaderData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str
    level: int

class QuoteData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str
    caption: str
    alignment: str

class ListItem(BaseModel):
    content: str
    meta: dict = {}
    items: List["ListItem"] 

class ListData(BaseModel):
    style: str
    meta: dict = {}
    items: List["ListItem"]

class Block(BaseModel):
    id: str
    type: str
    sequence: int | None = None 
    data: TableData | CodeToolData | ParagraphData | HeaderData | QuoteData | ListData

class BlockPub(BaseModel):
    '''
    This is a public block which will be sent
    to the frontend through EditorJSSessionDataPub
    '''
    model_config = ConfigDict(from_attributes=True)
    id: str 
    type: str 
    data: TableData | CodeToolData | ParagraphData | HeaderData | QuoteData | ListData

class EditorJSSessionData(BaseModel):
    time: int
    blocks: List[Block]
    version: str
    # logged_in_session_id: str
    # browser_session_id: str
    article_id: str

class EditorJSSessionDataPub(BaseModel):
    ''' 
    This model contains data which will be sent 
    to the frontend editorjs window.
    '''
    model_config = ConfigDict(from_attributes=True)
    time: int
    blocks: List[BlockPub]
    version: str

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
    text: str | None
    level: int = Field(default=1, frozen=True)

class SubtitleHeaderDataPub(BaseModel):
    text: str | None
    level: int = Field(default=3, frozen=True)

class TitleBlockPub(BaseModel):
    type: str = Field(default="title", frozen=True)
    data: TitleHeaderDataPub

class SubtitleBlockPub(BaseModel):
    type: str = Field(default="subtitle", frozen=True)
    data: SubtitleHeaderDataPub

class ArticleHeadPublic(BaseModel):
    blocks: tuple[TitleBlockPub, SubtitleBlockPub] = None