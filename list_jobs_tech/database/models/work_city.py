from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base_model import Base


class WorkCity(Base):
    __tablename__ = "work_city"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    job_offers = relationship("JobOffer", secondary="job_offers_work_cities", back_populates="work_cities")


class WorkCityResearchWebsiteAlias(Base):
    __tablename__ = "work_city_research_website_alias"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=True)
    work_city_id = Column(Integer, ForeignKey("work_city.id"))
    research_website_id = Column(Integer, ForeignKey("research_website.id"))
    __table_args__ = (UniqueConstraint("work_city_id", "research_website_id", name="uq_work_city_research_website"),)
