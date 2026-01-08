from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime
from . import user_model


class Tool(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    class_name: str 

    tool_mds: list["ToolMD"] | None = Relationship(back_populates="tool")


# class User(SQLModel, table=True):
#     id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key=True)
#     username: str = Field(unique=True)
#     email: str = Field(unique= True)
#     last_login: datetime | None = Field(default_factory=datetime.now)

#     articles: list["Article"] | None = Relationship(back_populates="author")


class Article(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key=True)
    title: str | None = Field(default=None)
    subtitle: str | None = Field(default=None)
    editor_session_id: uuid.UUID = Field(foreign_key="editor_session.id")
    pub_datetime: datetime = Field(default_factory= datetime.now)
    # path_url: str | None = Field(default=None)
    author_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    author: user_model.User | None = Relationship(back_populates="articles")
 
    '''
    article is either created during a session where 
    '''

    tool_mds: list["ToolMD"] | None = Relationship(back_populates="article")


class ToolMD(SQLModel, table=True): # Tool Meta Data
    id: uuid.UUID | None = Field(default_factory= uuid.uuid4, primary_key=True)
    sequence: int 
    block_id: str 

    article_id: uuid.UUID | None = Field(default=None, foreign_key="article.id")
    article: Article | None = Relationship(back_populates="tool_mds")

    tool_id: int = Field(default=None, foreign_key="tool.id")
    tool: Tool | None = Relationship(back_populates="tool_mds",\
                                     sa_relationship_kwargs={"lazy": "selectin"})

    __tablename__ = "tool_md"


# All the tool data model classes inherit this class
class ToolDataModel(SQLModel):
    pass

class EditorSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    logged_in: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    expiry_date: datetime | None = Field(default=None)
    browser_id: uuid.UUID = Field(default_factory=uuid.uuid4)

    __tablename__ = "editor_session"