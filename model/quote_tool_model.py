from sqlmodel import SQLModel, Field
import uuid
from .tool_model import ToolDataModel


class QuoteTool(ToolDataModel, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key= True)
    text: str
    caption: str
    alignment: str 

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "quote_tool"