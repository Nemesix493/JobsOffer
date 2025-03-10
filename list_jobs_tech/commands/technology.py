from argparse import ArgumentParser, Namespace
from json import (
    loads as json_load,
    JSONDecodeError
)

from sqlalchemy.exc import IntegrityError, NoResultFound

from .command import Command
from ..database import ManageDatabase
from ..database.models import Technology, TechnologyAlias


class TechnologyResourceCommand(Command):

    UNIQUE_KEYS = [
        'id',
        'name'
    ]

    @staticmethod
    def get_description() -> str:
        return "Manage the technologies"

    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        manage_ressource = parser.add_mutually_exclusive_group(required=True)
        manage_ressource.add_argument(
            "-l",
            "--list",
            dest="list",
            help="List the technologies",
            action="store_true"
        )
        manage_ressource.add_argument(
            "-d",
            "--detail",
            dest="detail",
            type=str,
            help="Detail a technology"
        )
        manage_ressource.add_argument(
            "-c",
            "--create",
            dest="create",
            type=str,
            help="Create a technology"
        )
        manage_ressource.add_argument(
            "-p",
            "--partial-update",
            dest="partial_update",
            type=str,
            help="Partial update a technology"
        )

    @classmethod
    def execute(cls, parsed_args: Namespace):
        if parsed_args.detail:
            return cls.detail_view(parsed_args.detail)
        elif parsed_args.list:
            return cls.list_view()
        elif parsed_args.create:
            return cls.create_view(parsed_args.create)
        elif parsed_args.partial_update:
            return cls.partial_update_view(parsed_args.partial_update)

    @classmethod
    def get_instance(cls, arg: str) -> Technology:
        arg_dict = cls.parse_json(arg)
        if arg_dict is None:
            return None
        for key in cls.UNIQUE_KEYS:
            if key in arg_dict.keys():
                try:
                    return (
                        ManageDatabase.get_session()
                        .query(Technology)
                        .filter(
                            getattr(Technology, key) == arg_dict[key]
                        ).one()
                    )
                except NoResultFound as e:
                    print(f'Technology not found !\n{e}')
                except Exception as e:
                    print(e)
        return None

    @staticmethod
    def parse_json(json_text: str) -> dict | None:
        try:
            detail_object = json_load(json_text)
        except JSONDecodeError as e:
            print(f"The send json is not correct\n\"{e}\"")
            return None
        if not isinstance(detail_object, dict):
            print("The json object must be a dict")
            return None
        aliases = detail_object.get('aliases', [])
        if not isinstance(aliases, list):
            print("The key \"aliases\" of the json object must be a list !")
            return None
        return detail_object

    @classmethod
    def detail_view(cls, detail_arg: str) -> None:
        instance = cls.get_instance(detail_arg)
        if instance is None:
            return None
        print(str(instance))

    @staticmethod
    def list_view() -> None:
        for technology in ManageDatabase.get_session().query(Technology).all():
            print(' - ' + str(technology).replace('\n', f"\n{4*' '}"))

    @classmethod
    def create_view(cls, create_arg: str) -> None:
        create_object = cls.parse_json(create_arg)
        if create_object is None:
            return None
        aliases = create_object.pop('aliases', [])
        try:
            technoloy_instance = Technology(**create_object)
            for alias in aliases:
                technoloy_instance.aliases.append(
                    TechnologyAlias(value=alias)
                )
            ManageDatabase.get_session().add(technoloy_instance)
            ManageDatabase.get_session().commit()
            print(str(technoloy_instance))
        except TypeError as e:
            print(e)
        except IntegrityError as e:
            print(e)
        except Exception as e:
            print(e)

    @classmethod
    def partial_update_view(cls, partial_update_arg) -> None:
        instance = cls.get_instance(partial_update_arg)
        partial_update_object = cls.parse_json(partial_update_arg)
        if partial_update_object is None:
            return None
        aliases = partial_update_object.pop('aliases', [])
        try:
            for key, val in partial_update_object.items():
                setattr(instance, key, val)
            for alias in aliases:
                instance.aliases.append(
                    TechnologyAlias(value=alias)
                )
            ManageDatabase.get_session().add(instance)
            ManageDatabase.get_session().commit()
            print(str(instance))
        except TypeError as e:
            print(e)
        except IntegrityError as e:
            print(e)
        except Exception as e:
            print(e)
