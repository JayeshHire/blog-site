from sqlmodel import SQLModel, Field
import uuid


class CodeTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str
    language_code: str

    tool_md_id: uuid.UUID = Field(foreign_key="tool_md.id")

    __tablename__ = "code_tool"