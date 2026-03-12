from pydantic import BaseModel


class SignupBaseModel(BaseModel):
    full_name: str 
    username: str
    email: str
    password: str 


class SigninBaseModel(BaseModel):
    username_or_email: str 
    password: str 
