from sqlmodel import SQLModel, Field
import uuid


class ParagraphTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str

