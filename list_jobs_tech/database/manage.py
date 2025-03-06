from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = 'sqlite:///my_db.db'

engine = create_engine(DB_PATH)

Session = sessionmaker(bind=engine)
