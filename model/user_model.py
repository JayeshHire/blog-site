from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, ValidationError
import uuid
from . import tool_model

class UserBase(SQLModel):
    full_name: str | None = None
    username: str | None = Field(default=None, unique=True)


class User(UserBase, table=True):
    # full_name: str | None 
    # username: str | None 
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str 
    articles: list["tool_model.Article"] | None = Relationship(back_populates="author")
    
    @field_validator('username', mode='before')
    @classmethod
    def validate_username(cls, value: str):
        if value is not None and '@' in value:
            raise ValueError(f"Username should not contain '@' symbol. Current value of username is `username={value}")
        return value
    

class UserPublic(UserBase):
    # full_name: str | None 
    # username: str | None
    email: str | None 


class UserCreate(UserBase):
    # full_name: str | None 
    # username: str | None
    email: str = Field(unique=True)
    password: str 