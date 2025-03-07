from pathlib import Path
from sqlite3 import connect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DB_PATH = 'sqlite:///my_db.db'


class ManageDatabase:
    @classmethod
    def get_engine(cls):
        if not hasattr(cls, '_engine'):
            cls._engine = create_engine(DB_PATH)
        return cls._engine

    @classmethod
    def get_session(cls):
        if not hasattr(cls, '_session'):
            cls._session = sessionmaker(bind=cls.get_engine())()
        return cls._session

    @classmethod
    def init_database(cls):
        Base.metadata.create_all(bind=cls.get_engine())
    
    @classmethod
    def destroy_database(cls):
        Base.metadata.drop_all(bind=cls.get_engine())

    @classmethod
    def dump_db(db_path: Path, dump_path: Path):
        conn = connect(db_path)
        with open(dump_path, "w") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()

    @classmethod
    def load_db(db_path: Path, dump_path: Path):
        pass
