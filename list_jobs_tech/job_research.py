import re
from typing import Generator

from bs4 import BeautifulSoup

from .delayed_requests import DelayedRequest as DelayedRequests
from .job_search_website import JobSearchWebSite
from .database import ResearchWebsite, JobOffer, WorkCity, WorkCityResearchWebsiteAlias, Session


class JobResearch:
    def __init__(self, website: ResearchWebsite, city: WorkCity, research_params: dict):
        self._website = website
        self._city = city
        self._research_params = research_params
        self._search_pages = None
        self._results = None
        self._session = None
        self._place = None
        self._delayed_requests = None

    @property
    def website(self) -> ResearchWebsite:
        return self._website

    @property
    def website_class(self):
        for subclass in JobSearchWebSite.__subclasses__():
            if subclass.__name__ == self.website.name:
                return subclass

    @property
    def city(self) -> WorkCity:
        self._city

    @property
    def place(self) -> WorkCityResearchWebsiteAlias:
        if self._place is None:
            self._place = self.session.query(
                WorkCityResearchWebsiteAlias
            ).filter(
                WorkCityResearchWebsiteAlias.research_website_id == self.website.id
            ).filter(
                WorkCityResearchWebsiteAlias.work_city_id == self.city.id
            ).one().value
        return self._place

    @property
    def research_params(self) -> dict:
        return self._research_params

    @property
    def session(self):
        if self._session is None:
            self._session = Session()
        return self._session

    def close_session(self):
        self.session.close()
        self._session = None

    def update_or_create_job_offer(self, offer_ID: str) -> JobOffer | None:
        """
        try to get object if got update it
        else create it
        """
        query = self.session.query(JobOffer).join(ResearchWebsite).join(WorkCity)
        job_offer = query.filter(
            JobOffer.website_id == offer_ID
        ).filter(
            JobOffer.research_website == self.website
        ).first()
        if job_offer is not None:
            if self.city not in job_offer.work_cities:
                job_offer.work_cities.append(self.city)
            self.session.add(job_offer)
            self.session.commit()
            return None
        job_offer = JobOffer(
            website_id=offer_ID,
            url=self.get_offer_url(offer_ID),
            description=self.get_description(offer_ID),
            research_website=self.website,
        )
        job_offer.work_cities.append(self.city)
        self.session.add(job_offer)
        self.session.commit()
        return job_offer

    @property
    def delayed_requests(self) -> DelayedRequests:
        if self._delayed_requests is None:
            self._delayed_requests = DelayedRequests(
                self.website.tempo_min,
                self.website.tempo_mean
            )
        return self._delayed_requests

    def get_results(self) -> None:
        self._results = int(re.match(
            "(^[0-9]*)",
            str(
                BeautifulSoup(
                    self.delayed_requests.get(
                        self.website_class.get_search_url(**self.research_params)
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

    @property
    def search_pages(self) -> list[dict]:
        if self._search_pages is None:
            self._search_pages = self.website_class.get_search_pages(
                self.research_params,
                self.results
            )
        return self._search_pages

    def get_offer_url(self, offer_ID) -> str:
        return self.website_class.get_offer_url(offer_ID)

    def get_description(self, offer_ID: str) -> str:
        response = self.delayed_requests.get(self.get_offer_url(offer_ID))
        if not response.ok:
            return None
        return BeautifulSoup(
            response.text,
            "html.parser"
        ).select_one("div.panel-container div.modal-body div.description").text

    def get_job_offers_ID(self) -> Generator[str, None, None]:
        for search_page in self.search_pages:
            response = self.delayed_requests.get(
                search_page['url']
            )
            if response.ok:
                nodes = BeautifulSoup(
                    response.text,
                    "html.parser"
                ).select(search_page['targets_nodes'])
                for node in nodes:
                    yield node[search_page['target_data']]

    @property
    def job_offers(self) -> list[JobOffer]:
        """
        return only the first seen offers of the research
        as JobOffer model object
        and update the others
        """
        if self._job_offers is None:
            self._job_offers = []
            for offer_ID in self.get_job_offers_ID():
                job_offer = self.update_or_create_job_offer(offer_ID)
                if job_offer is not None:
                    self._job_offers.append(job_offer)
            self.close_session()
        return self._job_offers
