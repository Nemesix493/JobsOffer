from sqlalchemy import create_engine

from .models import Base

DB_PATH = 'sqlite:///my_db.db'

def get_engine():
    return create_engine(DB_PATH)