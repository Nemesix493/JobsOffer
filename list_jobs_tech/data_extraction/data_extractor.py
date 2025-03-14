from requests import Response
from bs4 import BeautifulSoup

from .extraction_order import ExtractionOrder


class DataExtractor:

    @property
    def fields_order(self) -> dict[str, ExtractionOrder]:
        return self._fields_order

    def __init__(self, fields_order: dict[str, ExtractionOrder]):
        self.check_fields_order(fields_order)
        self._fields_order = fields_order

    def check_fields_order(self, fields_order: dict[str, ExtractionOrder]):
        for key, extraction_order in fields_order.items():
            if not isinstance(key, str):
                raise TypeError(f"{key} is not a string (str) !")
            is_extraction_order_subclass_instance = (
                isinstance(extraction_order, ExtractionOrder)
                and type(extraction_order) is not ExtractionOrder
            )
            if not is_extraction_order_subclass_instance:
                raise TypeError(
                    f"{key}: {extraction_order} is not an "
                    f"instance of ExtractionOrder subclass !"
                )
        return True

    def __call__(self, response: Response) -> dict:
        if response.ok:
            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )
            return {
                key: extraction_order(soup)
                for key, extraction_order in self.fields_order.items()
            }
        else:
            raise ValueError('Response is not OK !')
