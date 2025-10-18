from sqlmodel import SQLModel, Field
import uuid
from .tool_model import ToolDataModel


class HeaderTool(ToolDataModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    text: str
    level: int

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "header_tool"