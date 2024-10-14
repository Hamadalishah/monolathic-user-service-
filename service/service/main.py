import logging
from fastapi import FastAPI,Depends,HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session,select
from .model import User,update_user,token,RegisterUser
from .db import create_db_and_tables,get_session
from typing import Annotated
import asyncio
from .crud import register_user,auth_user,verify_password,user_patch_update
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from .authentication import current_user
from .authentication import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifspan event is started")
    logging.info("creating tables")
    try:
        await asyncio.to_thread(create_db_and_tables)
        logging.info("Tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
    yield
    # do something at shutdown
    
    
app = FastAPI(lifespan=lifespan,
               title="FastAPI Service",
               description="This is a FastAPI Service",
               version="0.0.1"
)

@app.get("/")
async def root():
    return {"message": "welcome to the user services"}

@app.post("/register")
async def register(user:RegisterUser,
                   session:Annotated[Session,Depends(get_session)]):
    new_user = await register_user(user=user,session=session)
    return new_user

@app.post("/token", response_model=token)
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                session:Annotated[Session,Depends(get_session)]):
    user = await auth_user(form_data.username,form_data.password,session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
@app.get('/user')
async def get_user(  session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(current_user)]):
    statement = select(User).where(User.id == current_user.id)
    statement1 = session.exec(statement).all()
    return statement1


@app.get('/user/{id}')
async def get_user_data_by_id(
    id: int,  
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(current_user)]
):
    
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this data")


    statement = select(User).where(User.id == id)
    user = session.exec(statement).first()


    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

   
    return user
@app.patch('/user/{id},{password}',response_model=User)
async def updated_user(
    id: int,edit_user:update_user, password:str, 
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(current_user)]):
    
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this data")
    
    match_user =select(User).where(User.id == id)
    statement = session.exec(match_user).first()
    if statement is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password,statement.password):
        raise HTTPException(status_code=403, detail="Yout password is incorrect please provide the correct password")
    statement1 = await user_patch_update(statement,edit_user)
    session.add(statement1)
    session.commit()
    session.refresh(statement1)
    return statement1

@app.delete('/user/{id}')
async def delete_user(id:int,password:str, 
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(current_user)]):
     
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this data")
    
    match_user =select(User).where(User.id == id)
    statement = session.exec(match_user).first()
    if statement is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password,statement.password):
        raise HTTPException(status_code=403, detail="You password is incorrect please provide the correct password")
    session.delete(statement)
    session.commit()
    return {"message":"User deleted successfully"}
