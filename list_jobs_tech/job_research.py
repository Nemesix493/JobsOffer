import re
from typing import Generator

from bs4 import BeautifulSoup

from .delayed_requests import DelayedRequest as DelayedRequests
from .database import ResearchWebsite, JobOffer, WorkCity, WorkCityResearchWebsiteAlias, ManageDatabase


class JobResearch:
    def __init__(self, website: ResearchWebsite, city: WorkCity, research_params: dict, max_new: int = 50):
        self._website = website
        self._city = city
        self._research_params = research_params
        self._search_pages = None
        self._results = None
        self._place = None
        self._delayed_requests = None
        self._job_offers = None
        self._max = max_new
        self.count = 0
        self._research_params['place'] = self.place

    @property
    def website(self) -> ResearchWebsite:
        return self._website

    @property
    def city(self) -> WorkCity:
        return self._city

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
        return ManageDatabase.get_session()

    def update_or_create_job_offer(self, offer_id: str) -> JobOffer | None:
        """
        try to get object if got update it
        else create it
        """
        query = self.session.query(JobOffer)
        job_offer = query.filter(
            JobOffer.website_id == offer_id
        ).filter(
            JobOffer.research_website == self.website
        ).first()
        if job_offer is not None:
            if self.city not in job_offer.work_cities:
                job_offer.work_cities.append(self.city)
            self.session.add(job_offer)
            self.session.commit()
            return None
        return self.get_job_offer(offer_id)

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
            "(^\d*)",  # noqa: W605
            str(
                BeautifulSoup(
                    self.delayed_requests.get(
                        self.website.job_search_website_class.get_search_url(**self.research_params)
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
            self._search_pages = self.website.job_search_website_class.get_search_pages(
                self.research_params,
                self.results
            )
        return self._search_pages

    def get_job_offer(self, offer_id) -> JobOffer:
        url = self.website.get_offer_url(offer_id)
        response = self.delayed_requests.get(url)
        job_offer = JobOffer(
            website_id=offer_id,
            url=url,
            research_website=self.website,
        )
        try:
            job_offer_dict = self.website.job_offer_extractor(response)
        except Exception as e:
            print(f"❌ {url}")
            print(e)
            return None
        print(f"✅ {url}")
        for key, val in job_offer_dict.items():
            setattr(
                job_offer,
                key,
                val
            )
        job_offer.work_cities.append(self.city)
        self.session.add(job_offer)
        self.session.commit()
        return job_offer

    def get_job_offers_id(self) -> Generator[str, None, None]:
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
            for offer_id in self.get_job_offers_id():
                if not self.is_under_max():
                    break
                job_offer = self.update_or_create_job_offer(offer_id)
                if job_offer is not None:
                    self.count += 1
                    self._job_offers.append(job_offer)
        return self._job_offers

    def is_under_max(self) -> bool:
        return self._max > self.count
