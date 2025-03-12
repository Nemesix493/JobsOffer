import re
from itertools import chain

from .job_research import JobResearch
from .database import JobOffer, Technology, ManageDatabase


class OffersAnalyser:
    @classmethod
    def replace_list(cls, text: str, char_list: list, char: str) -> str:
        if len(char_list) <= 0:
            return text
        else:
            return cls.replace_list(
                text.replace(
                    char_list[0],
                    char
                ),
                char_list[1:],
                char
            )

    @property
    def offers(self) -> list[JobOffer]:
        if self._offers is None:
            self._offers = list(chain(
                *[
                    job_research.job_offers
                    for job_research in self._research_list
                ]
            ))
        return self._offers

    @property
    def session(self):
        return ManageDatabase.get_session()

    @property
    def tech_by_aliases(self) -> dict[str: Technology]:
        if self._tech_by_aliases is None:
            self._tech_by_aliases = {}
            all_technologies = self.session.query(Technology).all()
            for technology in all_technologies:
                self._tech_by_aliases[technology.name] = technology
                for alias in technology.aliases:
                    self._tech_by_aliases[alias.value] = technology
        return self._tech_by_aliases

    def __init__(self, research_list: list[JobResearch]):
        self._research_list = research_list
        self._offers = None
        self._tech_by_aliases = None

    def analyse_offer_technologies(self, offer_description: str) -> list[Technology]:
        technologies = set()
        for pattern, technology in self.tech_by_aliases.items():
            if re.search(re.escape(pattern), offer_description, re.IGNORECASE):
                technologies.add(technology)
        return list(technologies)

    def analyse_offers(self) -> None:
        for offer in self.offers:
            offer.score = 0
            technologies = self.analyse_offer_technologies(offer.description)
            offer.score = sum([technology.skill_level for technology in technologies])
            for technology in technologies:
                if technology not in offer.technologies:
                    offer.technologies.append(technology)
            if len(offer.technologies) > 0:
                offer.score /= len(offer.technologies)
        self.session.add_all(self.offers)
        self.session.commit()

    def update_technologies(self):
        for technology in self.session.query(Technology).all():
            technology.average_score = 0
            for offer in technology.job_offers:
                technology.average_score += offer.score
            if len(technology.job_offers) > 0:
                technology.average_score /= len(technology.job_offers)
                technology.deepen_score = technology.average_score * (5 - technology.skill_level)
            self.session.add(technology)
        self.session.commit()
