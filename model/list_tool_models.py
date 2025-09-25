from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
import uuid
from typing import Dict, Any


class ListToolTbl(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    style: str
    meta: Dict[str, Any] = Field(sa_column=Column(JSON))

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "list_tool_tbl"


class ItemList(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lttbl_id: uuid.UUID = Field(foreign_key="list_tool_tbl.id") # list_tool_table

    __tablename__ = "item_list"

class Item(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sequence: int
    content: str
    meta: Dict[str, Any] = Field(sa_column=Column(JSON))
    child_item_list_id: uuid.UUID | None = Field(default=None, foreign_key="item_list.id")
    