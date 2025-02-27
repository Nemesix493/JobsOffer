from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

class JobSearchWebSite(ABC):
    _search_page = str()
    _result_target_node = str()
    _result_target_data = str()
    _search_page_param_aliases = dict()
    _search_page_param_default = dict()
    _search_page_targets_nodes = str()
    _search_page_target_data = str()
    _offer_base_url = str()

    @classmethod
    def get_search_url(cls, **search_params) -> str:
        url_params_dict = cls._search_page_param_default.copy()
        for key, val in search_params.items():
            if key in cls._search_page_param_aliases.keys():
                url_params_dict[
                    cls._search_page_param_aliases[key]
                ] = val
        url_params = "?" + '&'.join([
            f"{key}={val}"
            for key, val in url_params_dict.items()
        ])
        return cls._search_page + url_params
    
    @classmethod
    @abstractmethod
    def get_search_pages(cls, search_params, results: int):
        pass

    @classmethod
    def get_search_page_targets_nodes(cls, page_number: int = 0):
        return cls._search_page_targets_nodes
    
    @classmethod
    def get_offer_url(cls, offer_ID: str) -> str:
        return cls._offer_base_url + offer_ID



class FranceTravail(JobSearchWebSite):

    _search_page = "https://candidat.francetravail.fr/offres/recherche"
    _search_page_param_aliases = {
        "keyword": "motsCles",
        "place": "lieux",
        "radius_km": "rayon",
        "range": "range"
    }
    _search_page_param_default = {
        "tri": 0,
        "rayon": 10
    }
    _search_page_targets_nodes = "#page_0-19 li.result"
    _search_page_target_data = "data-id-offre"
    _offer_base_url = "https://candidat.francetravail.fr/offres/recherche/detail/"

    @classmethod
    def get_search_pages(cls, search_params: dict, results: int):
        search_params_copy = search_params.copy()
        number_page_result = results // 20
        search_pages = []
        if results % 20 != 0:
            number_page_result += 1
        for i in range(number_page_result):
            search_params_copy['range'] = f"{i * 20}-{(i + 1) * 20 - 1}"
            search_pages.append({
                'url': cls.get_search_url(**search_params_copy),
                'targets_nodes': cls._search_page_targets_nodes,
                'target_data': cls._search_page_target_data
            })
        return search_pages
