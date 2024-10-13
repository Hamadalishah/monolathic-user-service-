from fastapi import Form
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel,EmailStr
from typing import Annotated



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    email:str
    password: str
    
    
class update_user(BaseModel):
    user_name: str 
    email: EmailStr
    password: str 
    
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
    
class RegisterUser(BaseModel):
    
        user_name : Annotated[
            str,
            Form()
        ]
        email : Annotated[
            str,
            Form()
        ]
        password : Annotated[
            str,
            Form()
        ]
        
class token(BaseModel):
    access_token: str
    token_type: str