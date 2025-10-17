from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
import uuid
from typing import Any, Dict
from tool_model import ToolDataModel


class TableTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: Dict[str, Any] = Field(sa_column=Column(JSON))

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "table_tool"