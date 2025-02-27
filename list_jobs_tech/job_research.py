from bs4 import BeautifulSoup
import re

from .delayed_requests import tempo_requests_get, TEMPO_MEAN
from .job_search_website import JobSearchWebSite

class JobResearch:
    def __init__(self, website: JobSearchWebSite, research_params: dict):
        self._website = website
        self._research_params = research_params
        self._search_pages = None
        self._offers_pages_IDs = None
        self._results = None

    @property
    def website(self):
        return self._website

    def get_results(self):
        self._results = int(re.match(
            "(^[0-9]*)",
            str(
                BeautifulSoup(
                    tempo_requests_get(
                        self._website.get_search_url(**self._research_params)
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
        self._search_pages = self._website.get_search_pages(self._research_params, self.results)

    @property
    def search_pages(self) -> list[dict]:
        if self._search_pages is None:
            self.get_search_pages()
        return self._search_pages
    
    def get_offers_pages_IDs(self):
        self._offers_pages_IDs = []
        print(f"Load offer IDs will take {len(self.search_pages)*TEMPO_MEAN}s")
        for search_page in self.search_pages:
            response = tempo_requests_get(
                search_page['url']
            )
            if response.ok:
                nodes = BeautifulSoup(
                    response.text,
                    "html.parser"
                ).select(search_page['targets_nodes'])
                for node in nodes:
                    self._offers_pages_IDs.append(node[search_page['target_data']])
        print("Offer IDs loaded !")
    
    @property
    def offers_pages_IDs(self):
        if self._offers_pages_IDs is None:
            self.get_offers_pages_IDs()
        return self._offers_pages_IDs
    
    def get_offer_url(self, offer_ID):
        return self._website.get_offer_url(offer_ID)
    
    def get_description(self, offer_ID: str) -> str:
        response = tempo_requests_get(self.get_offer_url(offer_ID))
        if not response.ok:
            return None
        return BeautifulSoup(
            response.text,
            "html.parser"
        ).select_one("div.panel-container div.modal-body div.description").text