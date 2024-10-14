from typing import Annotated
from fastapi import FastAPI, Depends,HTTPException
from sqlmodel import Session,select
from .db import get_session
from  .model import User,update_user,RegisterUser
from passlib.context import CryptContext # type: ignore
from passlib.exc import UnknownHashError
from .authentication import current_user
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")




def verify_password(plain_password,password):
    try:
        
        return pwd_context.verify(plain_password,password)
    except UnknownHashError:
        print("Password hash could not be identified.")
def get_password_hash(password: str):
    return pwd_context.hash(password)





async def db_user(session: Annotated[Session, Depends(get_session)],
                   username: str | None = None,
                   email: str | None = None):
    statement = select(User).where(User.user_name == username)
    user = session.exec(statement).first()
    
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
    return user

async def auth_user(username:str| None ,password:str,
                     session: Annotated[Session, Depends(get_session)]
                                    ):
    data_user = await db_user(session=session,username=username)
    if not data_user:
        return False
    if not verify_password(password,data_user.password):
        return False
    return data_user
async def register_user(user:RegisterUser , session: Annotated[Session, Depends(get_session)]):
    existing_user = await db_user(username=user.user_name, email=user.email, session=session)  # Corrected call
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(user_name=user.user_name, email=user.email, password=get_password_hash(user.password))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


async def user_patch_update(statement,edit_user):
    if edit_user.user_name is not None and edit_user.user_name != "":
        statement.user_name = edit_user.user_name
    if edit_user.email is not None and edit_user.email != "":
        statement.email = edit_user.email
    if edit_user.password is not None and edit_user.password != "":
        statement.password = get_password_hash(edit_user.password)
    return statement
        
