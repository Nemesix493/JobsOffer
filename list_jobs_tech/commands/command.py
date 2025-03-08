from enum import Enum
from abc import abstractmethod
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import Type
import os


class Command:
    @staticmethod
    def get_default_parent() -> str:
        """Return basename of main script"""
        return os.path.basename(
            __import__('__main__').__file__
        )

    @classmethod
    def run(cls) -> None:
        parent = cls.get_default_parent()
        parser = ArgumentParser(
            description=cls.get_description(),
            formatter_class=RawTextHelpFormatter
        )
        cls.configure_parser(parent, parser)
        parsed_args = parser.parse_args()
        cls.execute(parsed_args)

    @staticmethod
    @abstractmethod
    def get_description() -> str:
        pass

    @classmethod
    @abstractmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        pass

    @classmethod
    @abstractmethod
    def execute(cls, parsed_args: Namespace) -> None:
        pass


class EnumCommand(Command, Enum):
    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest=cls.__name__, required=True)
        for command in cls:
            command_class = command.get_command_class()
            sub_parser = subparsers.add_parser(
                command.value,
                help=command_class.get_description() +
                f"\nFor more informations run -> {parent} {command.value} -h",
                description=command_class.get_description(),
                formatter_class=RawTextHelpFormatter
            )
            command_class.configure_parser(parent, sub_parser)

    @abstractmethod
    def get_command_class(self) -> Type[Command]:
        pass

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        """Run the execute method of the selected command"""
        selected_command = getattr(parsed_args, cls.__name__)
        cls(selected_command).get_command_class().execute(parsed_args)
