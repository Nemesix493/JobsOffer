import re
from itertools import chain

from sqlalchemy.orm import Session

from .job_research import JobResearch
from .database import JobOffer, Technology, ManageDatabase


class OffersAnalyser:

    # Static methods

    @staticmethod
    def get_session() -> Session:
        """Return the current database session."""
        return ManageDatabase.get_session()

    @staticmethod
    def set_offer_score(job_offer: JobOffer) -> None:
        """Calculate and set the score for a JobOffer based on the skill levels of its technologies."""
        job_offer.score = sum([technology.skill_level for technology in job_offer.technologies])
        technologies_length = len(job_offer.technologies)
        if technologies_length > 0:
            job_offer.score /= technologies_length

    @staticmethod
    def prevent_false_match_rule(pattern: str) -> str:
        """
        Ensure the pattern is preceded and followed by a non-alphanumeric boundary
        to prevent false matches.
        """
        return f"(?<!\\w){pattern}(?!\\w)"

    # Class methods

    @classmethod
    def apply_pattern_rules(cls, pattern: str) -> str:
        """Apply various rules to the pattern to prevent mismatches."""
        transformed_pattern = re.escape(pattern)
        transformed_pattern = cls.prevent_false_match_rule(transformed_pattern)
        return transformed_pattern

    @classmethod
    def all_technologies(cls) -> list[Technology]:
        """Load and return all Technologies from the database."""
        return cls.get_session().query(Technology).all()

    @classmethod
    def tech_by_aliases(cls) -> dict[str: Technology]:
        """Return a dictionary mapping technology names and aliases to their corresponding Technology objects."""
        if not hasattr(cls, "_tech_by_aliases"):
            setattr(cls, "_tech_by_aliases", {})
            for technology in cls.all_technologies():
                cls._tech_by_aliases[technology.name] = technology
                for alias in technology.aliases:
                    cls._tech_by_aliases[alias.value] = technology
        return cls._tech_by_aliases

    @classmethod
    def set_offer_technologies(cls, job_offer: JobOffer) -> list[Technology]:
        """
        Analyze the job offer description to identify and assign
        relevant technologies based on aliases and patterns.
        """
        technologies = set()
        for pattern, technology in cls.tech_by_aliases().items():
            if re.search(cls.apply_pattern_rules(pattern), job_offer.description, re.IGNORECASE):
                technologies.add(technology)
        job_offer.technologies = list(technologies)

    @classmethod
    def analyse_offers(cls, offers: list[JobOffer]) -> None:
        """Analyze a list of JobOffers by setting technologies and scores, then save them to the database."""
        for offer in offers:
            cls.set_offer_technologies(offer)
            cls.set_offer_score(offer)
        cls.get_session().add_all(offers)
        cls.get_session().commit()

    @classmethod
    def update_technologies(cls) -> None:
        """
        Calculate and update the scores for all technologies:
        - average_score based on job offer scores
        - deepen_score based on skill level and average_score
        """
        for technology in cls.all_technologies():
            technology.average_score = 0
            for offer in technology.job_offers:
                technology.average_score += offer.score
            if len(technology.job_offers) > 0:
                technology.average_score /= len(technology.job_offers)
                technology.deepen_score = technology.average_score * (5 - technology.skill_level)
            cls.get_session().add(technology)
        cls.get_session().commit()

    @classmethod
    def reanalyze(cls) -> None:
        """Reanalyze all data in the database, including JobOffers and Technologies."""
        cls.analyse_offers(
            cls.get_session().query(JobOffer).all()
        )
        cls.update_technologies()

    # Properties

    @property
    def offers(self) -> list[JobOffer]:
        """Return a list of all discovered JobOffers from the research chain."""
        if self._offers is None:
            self._offers = list(chain(
                *[
                    job_research.job_offers
                    for job_research in self._research_list
                ]
            ))
        return self._offers

    # Instance methods

    def __init__(self, research_list: list[JobResearch]):
        self._research_list = research_list
        self._offers = None

    def analyze(self) -> None:
        """Analyze all job offers from the research list and update technologies."""
        self.analyse_offers(self.offers)
        self.update_technologies()
