from argparse import ArgumentParser, Namespace

from sqlalchemy.exc import IntegrityError

from .ressource_command import RessourceCommand
from ..database import ManageDatabase
from ..database.models import Technology, TechnologyAlias
from ..offers_analyzer import OffersAnalyser


class TechnologyResourceCommand(RessourceCommand):

    UNIQUE_KEYS = [
        'id',
        'name'
    ]

    TABLE = Technology

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
    def parse_json(cls, json_text: str) -> dict | None:
        detail_object = super().parse_json(json_text)
        if detail_object is None:
            return None
        aliases = detail_object.get('aliases', [])
        if not isinstance(aliases, list):
            print("The key \"aliases\" of the json object must be a list !")
            return None
        return detail_object

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
            OffersAnalyser.reanalyze()
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
            OffersAnalyser.reanalyze()
            print(str(instance))
        except TypeError as e:
            print(e)
        except IntegrityError as e:
            print(e)
        except Exception as e:
            print(e)
