import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from ..services_config.config import DATABASE_URL

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL",DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,    
    pool_timeout=30,  
    pool_recycle=1800, 
    echo=False          
)

SessionLocal = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
