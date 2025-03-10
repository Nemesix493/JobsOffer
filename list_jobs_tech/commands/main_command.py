from .command import EnumCommand
from .research import ResearchCommand
from .report import ReportCommand
from .website import WebsiteResourceCommand
from .technology import TechnologyResourceCommand


class MainCommand(EnumCommand):
    make_research = "research"
    make_report = "report"
    manage_websites = "website"
    manage_technologies = "technology"

    def get_command_class(self):
        return {
            "research": ResearchCommand,
            "report": ReportCommand,
            "website": WebsiteResourceCommand,
            "technology": TechnologyResourceCommand
        }.get(self.value)

    @staticmethod
    def get_description():
        return "Main command description"
