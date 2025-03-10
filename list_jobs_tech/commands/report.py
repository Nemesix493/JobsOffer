from argparse import ArgumentParser, Namespace

from .command import Command
from ..report import Report


class ReportCommand(Command):
    @staticmethod
    def get_description() -> str:
        return "Return a report with :" \
            "\n    - the technologies you should learn (the technologies with a skill level = 0)" \
            "\n    - the technologies you should deepen (the technologies with a skill level > 0)" \
            "\n    - the best offers for you"

    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        pass

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        Report().report()
