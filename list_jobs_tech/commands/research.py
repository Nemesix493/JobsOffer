from argparse import ArgumentParser, Namespace

from .command import Command
from .command_mixin import JsonParseMixin
from ..job_research import JobResearch
from ..offers_analyzer import OffersAnalyser
from ..database import ManageDatabase
from ..database.models import WorkCity, ResearchWebsite


class ResearchCommand(Command, JsonParseMixin):
    @staticmethod
    def get_description() -> str:
        return "Run a web research !"

    @classmethod
    def configure_parser(cls, parent: str, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-p",
            "--research-params",
            dest="research_params",
            type=str,
            required=True,
            help="A json list of research params"
        )

    @staticmethod
    def get_city(name: str):
        return (
            ManageDatabase.get_session()
            .query(WorkCity)
            .filter(
                WorkCity.name == name
            ).one()
        )

    @staticmethod
    def get_website(name: str):
        return (
            ManageDatabase.get_session()
            .query(ResearchWebsite)
            .filter(
                ResearchWebsite.name == name
            ).one()
        )

    @classmethod
    def get_job_research(cls, research_params: dict):
        city_name = research_params.pop('city', None)
        website_name = research_params.pop('website', None)
        if None in (website_name, city_name):
            print("\"city\" and \"website\" are required !")
            return None
        max_new = research_params.pop('max_new', 50)
        return JobResearch(
            website=cls.get_website(website_name),
            city=cls.get_city(city_name),
            research_params=research_params,
            max_new=max_new
        )

    @classmethod
    def get_analyser(cls, json_text: str) -> OffersAnalyser | None:
        """Return OfferAnalyser from the given json or None in not valid"""
        json_object = cls.json_parse_validate(json_text, list[dict[str, str | int]])
        if json_object is None:
            return None
        return OffersAnalyser([
            cls.get_job_research(item)
            for item in json_object
        ])

    @classmethod
    def execute(cls, parsed_args: Namespace) -> None:
        """Execute the command from the parsed_args"""
        analyser = cls.get_analyser(parsed_args.research_params)
        if analyser is not None:
            analyser.analyze()
