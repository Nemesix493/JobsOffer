from pathlib import Path
from sqlite3 import connect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DB_PATH = Path(__file__).resolve().parent.parent.parent / "my_db.db"
INITIAL_DATA = Path(__file__).resolve().parent.parent.parent / "initial_data.sql"


class ManageDatabase:
    @classmethod
    def get_engine(cls):
        if not hasattr(cls, '_engine'):
            cls._engine = create_engine(f'sqlite:///{DB_PATH}')
        return cls._engine

    @classmethod
    def get_session(cls):
        if not hasattr(cls, '_session'):
            cls._session = sessionmaker(bind=cls.get_engine())()
        return cls._session

    @classmethod
    def init_database(cls):
        if not cls.is_db_exist():
            if INITIAL_DATA.exists() and INITIAL_DATA.is_file():
                cls.load_dump(INITIAL_DATA)
            else:
                Base.metadata.create_all(bind=cls.get_engine())

    @classmethod
    def destroy_database(cls):
        Base.metadata.drop_all(bind=cls.get_engine())

    @staticmethod
    def dump_db(dump_path: Path):
        conn = connect(DB_PATH)
        with open(dump_path, "w") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()

    @staticmethod
    def load_dump(dump_path: Path):
        conn = connect(DB_PATH)
        with open(dump_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
            conn.executescript(sql_script)
            conn.commit()
            conn.close()
    
    @staticmethod
    def is_db_exist():
        return DB_PATH.exists() and DB_PATH.is_file()
