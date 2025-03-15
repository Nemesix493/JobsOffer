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
        fields_choices = [field.value for field in Report.Fields]
        parser.add_argument(
            "--fields",
            type=str,
            nargs="*",
            choices=fields_choices,
            help="Fields to report (default: all if empty)"
        )

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        fields = set()
        if parsed_args.fields:
            for field_value in parsed_args.fields:
                fields.add(Report.Fields(field_value))
        report = Report(fields)
        print(report.text())
        if parsed_args.email:
            if isinstance(parsed_args.email, str):
                email_adresse = parsed_args.email
            else:
                email_adresse = None
            try:
                EmailSender(email_adresse).send_report(report)
            except ValueError as e:
                print(e)
