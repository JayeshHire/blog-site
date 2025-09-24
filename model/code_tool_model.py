from sqlmodel import SQLModel, Field
import uuid


class CodeTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str
    language_code: str

    tool_id: uuid.UUID = Field()