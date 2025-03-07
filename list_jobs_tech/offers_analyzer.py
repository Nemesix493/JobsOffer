from itertools import chain

from .job_research import JobResearch
from .settings import REMOVE_PATTERN
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
            print(self._tech_by_aliases.keys())
        return self._tech_by_aliases

    def __init__(self, research_list: list[JobResearch]):
        self._research_list = research_list
        self._offers = None
        self._tech_by_aliases = None

    def analyse_offers(self) -> None:
        for offer in self.offers:
            offer.score = 0
            word_list = self.replace_list(offer.description, REMOVE_PATTERN, " ").split(" ")
            for word in word_list:
                technology = self.tech_by_aliases.get(word.lower(), None)
                if technology is not None and technology not in offer.technologies:
                    offer.technologies.append(technology)
                    offer.score += technology.skill_level
            if len(offer.technologies) > 0:
                offer.score /= len(offer.technologies)
        self.session.add_all(self.offers)
        self.session.commit()
