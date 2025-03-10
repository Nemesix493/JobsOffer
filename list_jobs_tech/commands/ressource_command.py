from typing import Type, Optional, TypeVar
from json import loads, JSONDecodeError

from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.exc import NoResultFound

from .command import Command
from ..database import ManageDatabase


T = TypeVar("T", bound=DeclarativeMeta)


class RessourceCommand(Command):
    UNIQUE_KEYS = [
        'id',
    ]

    TABLE: Type[T]

    @staticmethod
    def get_session():
        return ManageDatabase.get_session()

    @classmethod
    def get_query(cls):
        return cls.get_session().query(cls.TABLE)

    @classmethod
    def get_instance(cls, arg: str) -> Optional[T]:
        arg_dict = cls.parse_json(arg)
        if arg_dict is None:
            return None
        for key in cls.UNIQUE_KEYS:
            if key in arg_dict.keys():
                try:
                    return (
                        cls.get_query()
                        .filter(
                            getattr(cls.TABLE, key) == arg_dict[key]
                        ).one()
                    )
                except NoResultFound as e:
                    print(f'{cls.TABLE.__name__} not found !\n{e}')
                except Exception as e:
                    print(e)
        return None

    @classmethod
    def parse_json(cls, json_text: str) -> dict | None:
        try:
            detail_object = loads(json_text)
        except JSONDecodeError as e:
            print(f"The send json is not correct\n\"{e}\"")
            return None
        if not isinstance(detail_object, dict):
            print("The json object must be a dict")
            return None
        return detail_object

    @classmethod
    def list_view(cls) -> None:
        for instance in cls.get_query().all():
            print(' - ' + str(instance).replace('\n', f"\n{7*' '}"))

    @classmethod
    def detail_view(cls, detail_arg: str) -> None:
        instance = cls.get_instance(detail_arg)
        if instance is None:
            return None
        print(str(instance))
