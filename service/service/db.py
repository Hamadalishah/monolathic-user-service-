from sqlmodel import SQLModel, create_engine,Session
from dotenv import load_dotenv # type: ignore
from typing import Optional
import os
load_dotenv()
connection_string: Optional[str] = os.environ.get("DATABASE_URL")
print(f"Connection string: {connection_string}")

if connection_string is None:
    raise ValueError("DATABASE_URL is not set in the environment variables")
engine = create_engine(connection_string)

def create_db_and_tables():
    print(f"Engine: {engine}")
    
    SQLModel.metadata.create_all(engine)
    
def get_session():
    # create a new Session
    session = Session(engine)
    yield session
    
    