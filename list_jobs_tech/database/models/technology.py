from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from .base_model import Base


class Technology(Base):
    __tablename__ = "technology"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    skill_level = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0, nullable=False)
    deepen_score = Column(Float, default=0, nullable=False)
    aliases = relationship("TechnologyAlias", back_populates="technology")
    job_offers = relationship("JobOffer", secondary="job_offers_technologies", back_populates="technologies")

    def __str__(self) -> str:
        str_result = (
            f"id: {self.id}\n"
            f"name: {self.name}\n"
            f"skill_level: {self.skill_level}\n"
            f"average_score: {self.average_score}\n"
            f"deepen_score: {self.deepen_score}"
        )
        if len(self.aliases) > 0:
            str_result += "\naliases:"
            for alias in self.aliases:
                str_result += f"\n{4*' '}- {alias.value}"
        return str_result


class TechnologyAlias(Base):
    __tablename__ = "technology_alias"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, index=True, nullable=False)
    technology_id = Column(Integer, ForeignKey("technology.id"), nullable=False)
    technology = relationship("Technology", back_populates="aliases")
