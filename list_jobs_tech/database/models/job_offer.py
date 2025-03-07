from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship

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
    technologies = relationship("Technology", secondary="job_offers_technologies", back_populates="job_offers")
    work_cities = relationship("WorkCity", secondary="job_offers_work_cities", back_populates="job_offers")

    research_website_id = Column(Integer, ForeignKey("research_website.id"))
    research_website = relationship("ResearchWebsite", back_populates="job_offers")

    __table_args__ = (UniqueConstraint("website_id", "research_website_id", name="uq_website_id_research_website"),)


class JobOffersTechnologies(Base):
    __tablename__ = "job_offers_technologies"
    id = Column(Integer, primary_key=True, index=True)
    job_offer_id = Column(Integer, ForeignKey("job_offer.id"))
    technology_id = Column(Integer, ForeignKey("technology.id"))


class JobOffersWorkCities(Base):
    __tablename__ = "job_offers_work_cities"
    id = Column(Integer, primary_key=True, index=True)
    job_offer_id = Column(Integer, ForeignKey("job_offer.id"))
    work_city_id = Column(Integer, ForeignKey("work_city.id"))
