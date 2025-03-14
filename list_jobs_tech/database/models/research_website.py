from typing import Type
from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import relationship

from .base_model import Base
from ...data_extraction import DataExtractor, ExtractString, ExtractDate
from ...job_search_website import JobSearchWebSite


class ResearchWebsite(Base):
    __tablename__ = "research_website"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    tempo_min = Column(Integer, nullable=False)
    tempo_mean = Column(Integer, nullable=False)
    job_offers = relationship("JobOffer", back_populates="research_website")
    description_node_selector = Column(String, nullable=False)
    description_target_data = Column(String, nullable=False)
    title_node_selector = Column(String, nullable=False)
    title_target_data = Column(String, nullable=False)
    add_date_node_selector = Column(String, nullable=True)
    add_date_target_data = Column(String, nullable=True)
    add_date_regex = Column(String, nullable=True)
    add_date_date_field_order = Column(String, nullable=True)
    search_page = Column(String, nullable=True)
    offer_base_url = Column(String, nullable=True)

    def __str__(self) -> str:
        return (
            f"id: {self.id}\n"
            f"name: {self.name}\n"
            f"tempo_min: {self.tempo_min}\n"
            f"tempo_mean: {self.tempo_mean}\n"
            f"job_offers: {len(self.job_offers)}"
        )

    @property
    def job_offer_extractor(self) -> DataExtractor:
        if hasattr(self, '_job_offer_extractor'):
            return self._job_offer_extractor
        extractions = {
            'description': ExtractString(
                self.description_node_selector,
                self.description_target_data
            ),
            'title': ExtractString(
                self.title_node_selector,
                self.title_target_data
            )
        }
        add_date_extraction_fields = [
            self.add_date_node_selector,
            self.add_date_target_data,
            self.add_date_regex,
            self.add_date_date_field_order
        ]
        if all(field is not None for field in add_date_extraction_fields):
            extractions['add_date'] = ExtractDate(
                    self.add_date_node_selector,
                    self.add_date_target_data,
                    self.add_date_regex,
                    tuple(
                        ExtractDate.DateField(date_field)
                        for date_field in self.add_date_date_field_order.split(',')
                    )
                )
        setattr(self, '_job_offer_extractor', DataExtractor(extractions))
        return self._job_offer_extractor

    def get_offer_url(self, offer_id):
        return self.offer_base_url.format(offer_id=offer_id)

    @property
    def job_search_website_class(self) -> Type[JobSearchWebSite]:
        if not hasattr(self, '_job_search_webSite_class'):
            for subclass in JobSearchWebSite.__subclasses__():
                if subclass.__name__ == self.name:
                    setattr(
                        self,
                        '_job_search_webSite_class',
                        subclass
                    )
        return self._job_search_webSite_class


@event.listens_for(ResearchWebsite, "before_insert")
@event.listens_for(ResearchWebsite, "before_update")
def validate_logic_object(mapper, connection, target):
    """Prevents saving if the job_offer_extractor construction fails"""
    try:
        _ = target.job_offer_extractor
    except Exception as e:
        raise ValueError(
            "Validation error can't create"
            " job_offer_extractor due to previous error"
        ) from e
