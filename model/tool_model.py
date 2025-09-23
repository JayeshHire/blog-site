from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime


class Tool(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    class_name: str 

    tool_mds: list["ToolMD"] | None = Relationship(back_populates="tool")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique= True)
    last_login: datetime | None

    articles: list["Article"] | None = Relationship(back_populates="author")


class Article(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key=True)
    title: str
    subtitle: str
    pub_datetime: datetime = Field(default_factory= datetime.now)

    author_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    author: User | None = Relationship(back_populates="articles")

    tool_mds: list["ToolMD"] | None = Relationship(back_populates="article")


class ToolMD(SQLModel, table=True): # Tool Meta Data
    id: uuid.UUID | None = Field(default_factory= uuid.uuid4, primary_key=True)
    sequence: int 
    block_id: uuid.UUID

    article_id: uuid.UUID | None = Field(default=None, foreign_key="article.id")
    article: Article | None = Relationship(back_populates="tool_mds")

    tool_id: uuid.UUID | None = Field(default=None, foreign_key="tool.id")
    tool: Tool | None = Relationship(back_populates="tool_mds")