from sqlmodel import SQLModel, Field
import uuid


class QuoteTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key= True)
    text: str
    caption: str
    alignment: str 