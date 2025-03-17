from sqlalchemy import desc, func
from jinja2 import Environment, FileSystemLoader
from enum import Enum

from .database import JobOffer, Technology, ManageDatabase
from .settings import TEMPLATES_DIR


class Report:
    class Fields(Enum):
        SHOULD_LOOK = 'should-look'
        SHOULD_LEARN = 'should-learn'
        SHOULD_DEEPEN = 'should-deepen'

    def __init__(self, fields: set[Fields]):
        """Set up the fields wanted in the report"""
        if not all(isinstance(field, self.Fields) for field in fields):
            raise TypeError("fields must be instance of Report.Fields !")
        self._fields = fields
        if len(self._fields) == 0:
            for field in self.Fields:
                self._fields.add(field)

    @property
    def session(self):
        return ManageDatabase.get_session()

    @property
    def should_learn(self) -> list[Technology]:
        """Return the top two technologies you should learn"""
        if not hasattr(self, "_should_should_learn_deepen"):
            setattr(
                self,
                "_should_learn",
                (
                    self.session.query(Technology)
                    .filter(Technology.skill_level == 0)
                    .order_by(desc(Technology.average_score))
                    .limit(2).all()
                )
            )
        return getattr(self, "_should_learn")

    @property
    def should_deepen(self) -> list[Technology]:
        """Return the top five technologies you should deepen"""
        if not hasattr(self, "_should_deepen"):
            setattr(
                self,
                "_should_deepen",
                (
                    self.session.query(Technology)
                    .filter(Technology.skill_level > 0)
                    .order_by(desc(Technology.deepen_score))
                    .limit(5).all()
                )
            )
        return getattr(self, "_should_deepen")

    def set_offers_as_reported(self, offers: list[JobOffer]) -> None:
        """
        Set a list of JobOffers as reported in the database,
         preventing them from being reported in future reports.
        """
        for offer in offers:
            offer.reported = True
            self.session.add(offer)
        self.session.commit()

    def get_should_look(self):
        """Return the top five JobOffers from the database according to report criteria."""
        max_last_seen_date = self.session.query(
            func.max(JobOffer.last_seen_date)
        ).scalar_subquery()
        max_time_adjusted = self.session.query(
            func.max(JobOffer.time_adjusted)
        ).scalar_subquery()
        reported_offer = (
            self.session.query(
                JobOffer,
                (
                    (3 * JobOffer.score + (10 * JobOffer.time_adjusted / max_time_adjusted)) / 5
                ).label('time_adjusted_score')
            ).filter(JobOffer.last_seen_date == max_last_seen_date)
            .filter(JobOffer.score >= 3)
            .filter(JobOffer.reported is not True)
            .order_by(desc('time_adjusted_score'))
            .limit(5).all()
        )
        should_look = []
        for job_offer, time_adjusted_score in reported_offer:
            job_offer.set_time_adjusted_score = time_adjusted_score
            should_look.append(job_offer)
        self.set_offers_as_reported(should_look)
        return should_look

    @property
    def should_look(self) -> list[JobOffer]:
        """Return the top five Jobs Offers you should look"""
        if not hasattr(self, "_should_look"):
            setattr(
                self,
                "_should_look",
                self.get_should_look()
            )
        return getattr(self, "_should_look")

    @property
    def context(self) -> dict:
        """Return the context for the templates"""
        return {
            field.value.replace('-', '_'): getattr(self, field.value.replace('-', '_'))
            for field in self._fields
        }

    def html(self) -> str:
        """Return html format report"""
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("report.html")
        result = template.render(self.context)
        env.cache.clear()
        return result

    def text(self) -> str:
        """Return text format report"""
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("report.txt")
        result = template.render(self.context)
        env.cache.clear()
        return result
