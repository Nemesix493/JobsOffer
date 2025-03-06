from bs4 import BeautifulSoup
import re

from .delayed_requests import DelayedRequest
from .job_search_website import JobSearchWebSite
from .database import ResearchWebsite, JobOffer


TEMPO_MEAN = 10
TEMPO_MIN = 4

tempo_requests = DelayedRequest(TEMPO_MIN, TEMPO_MEAN)


class JobResearch:
    def __init__(self, website: ResearchWebsite, research_params: dict):
        self._website = website
        self._research_params = research_params
        self._search_pages = None
        self._offers_pages_IDs = None
        self._results = None

    @property
    def website(self) -> ResearchWebsite:
        return self._website

    @property
    def website_class(self):
        for subclass in JobSearchWebSite.__subclasses__():
            if subclass.__name__ == self.website.name:
                return subclass

    def get_results(self):
        self._results = int(re.match(
            "(^[0-9]*)",
            str(
                BeautifulSoup(
                    tempo_requests.get(
                        self.website_class.get_search_url(**self._research_params)
                    ).text,
                    "html.parser"
                ).select_one("#zoneAfficherListeOffres h1.title").text
            ).replace('\n', '')
        ).groups()[0])

    @property
    def results(self) -> int:
        if self._results is None:
            self.get_results()
        return self._results
    
    def get_search_pages(self):
        self._search_pages = self.website_class.get_search_pages(self._research_params, self.results)

    @property
    def search_pages(self) -> list[dict]:
        if self._search_pages is None:
            self.get_search_pages()
        return self._search_pages
    
    def get_offer_url(self, offer_ID):
        return self.website_class.get_offer_url(offer_ID)
    
    def get_description(self, offer_ID: str) -> str:
        response = tempo_requests.get(self.get_offer_url(offer_ID))
        if not response.ok:
            return None
        return BeautifulSoup(
            response.text,
            "html.parser"
        ).select_one("div.panel-container div.modal-body div.description").text
    
    def get_offers_pages_IDs(self):
        self._offers_pages_IDs = []
        self._job_offers = []
        print(f"Load offer IDs will take {len(self.search_pages)*TEMPO_MEAN}s")
        for search_page in self.search_pages:
            response = tempo_requests.get(
                search_page['url']
            )
            if response.ok:
                nodes = BeautifulSoup(
                    response.text,
                    "html.parser"
                ).select(search_page['targets_nodes'])
                for node in nodes:
                    offer_ID = node[search_page['target_data']]
                    self._offers_pages_IDs.append(offer_ID)
                    self._job_offers = JobOffer(
                        website_id=offer_ID,
                        url=self.get_offer_url(offer_ID),
                        description=self.get_description(offer_ID),
                        research_website=self.website
                    )
        print("Offer IDs loaded !")
    
    @property
    def offers_pages_IDs(self):
        if self._offers_pages_IDs is None:
            self.get_offers_pages_IDs()
        return self._offers_pages_IDs
    
    @property
    def job_offers(self) -> list[JobOffer]:
        """
        return all the offers of the research
        as JobOffer model object
        """
        if self._job_offers is None:
            self.get_offers_pages_IDs()
        return self._job_offers
