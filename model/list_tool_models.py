from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy.types import JSON
import uuid
from typing import Dict, Any, List
from .tool_model import ToolDataModel

class ListToolTbl(ToolDataModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    style: str
    meta: Dict[str, Any] = Field(sa_column=Column(JSON))
    # sequence: int | None = Field(default= None)

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "list_tool_tbl"


# class ItemList(SQLModel, table=True):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     lttbl_id: uuid.UUID = Field(foreign_key="list_tool_tbl.id") # list_tool_table

#     # this field shows that this list is a list inside another item
#     parent_item_id: uuid.UUID | None = Field(default= None, foreign_key= "item.id") 
#     __tablename__ = "item_list"


class Item(ToolDataModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lttbl_id: uuid.UUID | None = Field(foreign_key="list_tool_tbl.id") # list_tool_table
    sequence: int 
    content: str
    meta: Dict[str, Any] = Field(sa_column=Column(JSON))
    
    # parent_item_list_id: uuid.UUID = Field(default=None, foreign_key="item_list.id")
    
    # parent item id will be None in case where the item directly belongs to the main item list
    parent_item_id: uuid.UUID | None = Field(default= None, foreign_key="item.id")
