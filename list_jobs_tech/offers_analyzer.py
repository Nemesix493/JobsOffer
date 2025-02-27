from .job_research import JobResearch
from .models import Techno, Offers, Abilities
from .settings import REMOVE_PATTERN

class OffersAnalyser:

    TECHNO_DB = Techno("test")
    ABILITIES_DB = Abilities("test")

    MAX_OFFERS = 100
    MAX_OFFERS_PER_RESEARCH = 50
    OFFER_MIN_SCORE = 0.1

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
    def offers(self) -> list[dict[str: str]]:
        if self._offers is None:
            self.get_offers()
        
        return self._offers

    @property
    def tech_list(self) -> list:
        return list(self.TECHNO_DB.data.keys())
    
    @property
    def abilities(self) -> dict:
        return self.ABILITIES_DB._data
    
    @property
    def technologies(self) -> dict:
        return self.TECHNO_DB.data
    
    @property
    def not_max(self):
        if self.MAX_OFFERS is not None:
            is_total_counter_ok = self._total_counter < self.MAX_OFFERS
        else:
            is_total_counter_ok = True
        if self.MAX_OFFERS_PER_RESEARCH is not None:
            is_research_counter_ok = self._research_counter < self.MAX_OFFERS_PER_RESEARCH
        else:
            is_research_counter_ok = True

        return  is_total_counter_ok and is_research_counter_ok

    def __init__(self, research_list: list[JobResearch]):
        self._research_list = research_list
        self._offers = None
        self._websites_db = None
        self._total_counter = 0
        self._research_counter = 0
    
    def increment_counters(self):
        self._total_counter += 1
        self._research_counter += 1
    
    def reset_research_counter(self):
        self._research_counter = 0
    
    def get_website_db(self):
        self._websites_db = {}
        for research in self._research_list:
            website_name = research.website.__name__
            if website_name not in self._websites_db.keys():
                self._websites_db[website_name]=Offers(website_name)
    
    def load_custom_website_db(self, db_names: list[str]):
        self._websites_db = {}
        for db_name in db_names:
            if db_name not in self.websites_db.keys():
                self._websites_db[db_name] = Offers(db_name)

    
    @property
    def websites_db(self):
        if self._websites_db is None:
            self.get_website_db()
        return self._websites_db


    def get_offers_from_research(self, research: JobResearch) -> list:
        offer_db = self.websites_db[research.website.__name__].data
        result = []
        for offer_ID in research.offers_pages_IDs:
            if offer_ID not in offer_db.keys() and self.not_max:
                description = research.get_description(offer_ID)
                if description is not None:
                    self.increment_counters()
                    result.append({
                        'ID': offer_ID,
                        'description': description,
                        'url': research.get_offer_url(offer_ID),
                        'website': research.website.__name__
                    })
                    print(f"Offer n°{self._total_counter} loaded !")
        self.reset_research_counter()
        return result

    def get_offers(self):
        self._offers = []
        for research in self._research_list:
            self._offers += self.get_offers_from_research(research)
    
    def add_offer_tech_list(self, offer: dict) -> dict:
        word_list = self.replace_list(offer['description'], REMOVE_PATTERN, " ").split(" ")
        offer['tech_list'] = []
        for word in word_list:
            word_lower = word.lower()
            if word_lower in self.tech_list and word_lower not in offer['tech_list']:
                offer['tech_list'].append(word_lower)
        return offer
    
    def add_offer_score(self, offer: dict) -> dict:
        offer['score'] = 0.0
        if len(offer['tech_list']) > 0:
            for tech in offer['tech_list']:
                if tech in self.abilities.keys():
                    offer['score'] += self.abilities[tech]
            offer['score'] /= len(offer['tech_list'])
        return offer
    
    def update_tech_list(self, offer: dict):
        for tech in offer['tech_list']:
            self.TECHNO_DB.data[tech] += 1
    
    def analyse_offer(self, offer: dict) -> dict:
        self.add_offer_tech_list(offer)
        self.add_offer_score(offer)
        self.update_tech_list(offer)
        return offer
    
    def analyse_offers(self, offers: list):
        self._offers = [
            self.analyse_offer(offer)
            for offer in offers
        ]
    
    def save(self):
        self.ABILITIES_DB.save()
        self.TECHNO_DB.save()
        for offer in self.offers:
            self.websites_db[
                offer['website']
            ].data[
                offer['ID']
            ] = offer
        for website_db in self.websites_db.values():
            website_db.save()
    
    def report_should_learn(self):
        not_know_tech_list = [
            tech
            for tech in self.technologies.keys()
            if tech not in self.abilities.keys()
        ]
        return sorted(
            not_know_tech_list,
            key=lambda key: self.technologies[key],
            reverse=True
        )[:5]
    
    def report_should_deepen(self):
        should_deepen = [
            ability
            for ability in self.abilities.keys()
            if self.abilities[ability] <= 2
        ]
        return sorted(
            should_deepen,
            key=lambda key: self.technologies[key],
            reverse=True
        )[:5]
    
    def report_should_look(self):
        should_look = [
            offer
            for offer in self.offers
            if offer['score'] >= self.OFFER_MIN_SCORE
        ]
        return sorted(
            should_look,
            key=lambda offer: offer['score'],
            reverse=True
        )[:10]
    
    def report(self):
        print('You should learn :')
        for tech in self.report_should_learn():
            print(f"    - {tech} : {self.technologies[tech]}")
        print('You should deepen :')
        for tech in self.report_should_deepen():
            print(f"    - {tech} : {self.technologies[tech]} {self.abilities[tech]}")
        print("You should look :")
        for offer in self.report_should_look():
            print(f"    - {offer['score']} : ")
            print(f"{8*' '}{offer['tech_list']}")
            print(f"{8*' '}{offer['url']}")

    def run_end_to_end(self):
        self.analyse_offers(self.offers)
        self.save()
        self.report()
    
    def reanalyse_offers(self, db_names):
        self.TECHNO_DB.reset()
        self.load_custom_website_db(db_names)
        offers = []
        for website_db in self.websites_db.values():
            offers += list(website_db.data.values())
        self.analyse_offers(offers)
        self.save()
        self.report()



    

