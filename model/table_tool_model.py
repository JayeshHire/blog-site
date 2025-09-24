from sqlmodel import SQLModel, Field, Column
from sqlalchemy.types import JSON
import uuid
from typing import Any, Dict


class TableTool(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: Dict[str, Any] = Field(sa_column=Column(JSON))
