from sqlmodel import SQLModel, Field
import uuid
from tool_model import ToolDataModel


class ParagraphTool(ToolDataModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "paragraph_tool"