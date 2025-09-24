from sqlmodel import SQLModel, Field
import uuid


class HeaderTool(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    text: str
    level: int
