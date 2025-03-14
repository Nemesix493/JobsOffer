from argparse import ArgumentParser, Namespace

from .ressource_command import RessourceCommand
from ..database.models import ResearchWebsite


class WebsiteResourceCommand(RessourceCommand):
    UNIQUE_KEYS = [
        'id',
        'name'
    ]

    TABLE = ResearchWebsite

    @staticmethod
    def get_description() -> str:
        return "Manage the websites"

    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        manage_ressource = parser.add_mutually_exclusive_group(required=True)
        manage_ressource.add_argument(
            "-l",
            "--list",
            dest="list",
            help="List the websites",
            action="store_true"
        )
        manage_ressource.add_argument(
            "-d",
            "--detail",
            dest="detail",
            type=str,
            help="Detail a website"
        )

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        if parsed_args.list:
            return cls.list_view()
        elif parsed_args.detail:
            return cls.detail_view(parsed_args.detail)
