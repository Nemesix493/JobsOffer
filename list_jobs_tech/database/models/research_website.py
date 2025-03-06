from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base_model import Base


class ResearchWebsite(Base):
    __tablename__ = "research_website"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    tempo_min = Column(String, nullable=False)
    tempo_mean = Column(String, nullable=False)
    job_offers = relationship("JobOffer", back_populates="research_website")
