from .job_search_website import FranceTravail
from .job_research import JobResearch
from .offers_analyzer import OffersAnalyser

def run():
    OffersAnalyser([
        JobResearch(
            website=FranceTravail,
            research_params={
                'place': '44109',
                'keyword': 'Python',
                'radius_km': 20
            }
        ),
        JobResearch(
            website=FranceTravail,
            research_params={
                'place': '49099',
                'keyword': 'Python',
                'radius_km': 30
            }
        ),
        JobResearch(
            website=FranceTravail,
            research_params={
                'place': '49007',
                'keyword': 'Python',
                'radius_km': 20
            }
        )
    ]).run_end_to_end()

__all__ = [
    "run",
]