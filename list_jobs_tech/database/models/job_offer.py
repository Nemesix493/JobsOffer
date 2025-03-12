from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, func, UniqueConstraint, Table, Boolean
from sqlalchemy.orm import relationship, column_property

from .base_model import Base


class JobOffer(Base):
    __tablename__ = "job_offer"
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(String, index=True, nullable=False)
    add_date = Column(Date, default=func.current_date(), nullable=False)
    last_seen_date = Column(Date, default=func.current_date(), onupdate=func.current_date(), nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)
    score = Column(Float, default=0, nullable=False)
    reported = Column(Boolean, default=False, nullable=False)
    time_adjusted = column_property(
        (func.julianday(last_seen_date) - func.julianday(add_date)) + 1
    )
    technologies = relationship("Technology", secondary="job_offers_technologies", back_populates="job_offers")
    work_cities = relationship("WorkCity", secondary="job_offers_work_cities", back_populates="job_offers")

    research_website_id = Column(Integer, ForeignKey("research_website.id"))
    research_website = relationship("ResearchWebsite", back_populates="job_offers")

    __table_args__ = (UniqueConstraint("website_id", "research_website_id", name="uq_website_id_research_website"),)

    @property
    def time_adjusted_score(self):
        if hasattr(self, '_time_adjusted_score'):
            return self._time_adjusted_score
        else:
            return None

    @time_adjusted_score.setter
    def set_time_adjusted_score(self, time_adjusted_score: float):
        setattr(self, '_time_adjusted_score', time_adjusted_score)


JobOffersTechnologies = Table(
    "job_offers_technologies",
    Base.metadata,
    Column("job_offer_id", ForeignKey("job_offer.id"), primary_key=True),
    Column("technology_id", ForeignKey("technology.id"), primary_key=True)
)


JobOffersWorkCities = Table(
    "job_offers_work_cities",
    Base.metadata,
    Column("job_offer_id", ForeignKey("job_offer.id"), primary_key=True),
    Column("work_city_id", ForeignKey("work_city.id"), primary_key=True)
)
