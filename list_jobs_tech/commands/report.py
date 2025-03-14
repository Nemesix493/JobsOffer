from argparse import ArgumentParser, Namespace

from .command import Command
from ..report import Report
from ..email_sender import EmailSender


class ReportCommand(Command):
    @staticmethod
    def get_description() -> str:
        return "Return a report with :" \
            "\n    - the technologies you should learn (the technologies with a skill level = 0)" \
            "\n    - the technologies you should deepen (the technologies with a skill level > 0)" \
            "\n    - the best offers for you"

    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-e",
            "--email",
            nargs="?",
            dest="email",
            const=True,
            help="Send the report to EMAIL adresse\n"
            "Without EMAIL specify send to the default email"
            " if configured"
        )

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        report = Report()
        report.print_report()
        if parsed_args.email:
            if isinstance(parsed_args.email, str):
                email_adresse = parsed_args.email
            else:
                email_adresse = None
            try:
                EmailSender(email_adresse).send_report(report)
            except ValueError as e:
                print(e)
