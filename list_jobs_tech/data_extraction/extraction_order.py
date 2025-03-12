import re
from abc import ABC
from enum import Enum
from datetime import date

from bs4 import BeautifulSoup


class ExtractionOrder(ABC):
    @property
    def node_selector(self) -> str:
        return self._node_selector

    @property
    def target_data(self) -> str:
        return self._target_data

    @property
    def multiple_node(self) -> bool:
        return self._multiple_node

    def get_node(self, soup: BeautifulSoup):
        return soup.select_one(self.node_selector)

    def get_nodes(self, soup: BeautifulSoup):
        return soup.select(self.node_selector)

    def get_data(self, node):
        if self.target_data == 'text':
            return getattr(node, 'text', None)
        else:
            return node.get(self.target_data, None)

    def transform_data(self, data: str):
        return data

    def __call__(self, soup: BeautifulSoup):
        if self.multiple_node:
            return [
                self.transform_data(
                    self.get_data(node)
                )
                for node in self.get_nodes(soup)
            ]
        else:
            return self.transform_data(
                self.get_data(
                    self.get_node(soup)
                )
            )


class ExtractString(ExtractionOrder):
    def __init__(self, node_selector: str, target_data: str):
        self._node_selector = node_selector
        self._target_data = target_data
        self._multiple_node = False


class ExtractStringList(ExtractionOrder):
    def __init__(self, node_selector: str, target_data: str, multiple_node: bool):
        self._node_selector = node_selector
        self._target_data = target_data
        self._multiple_node = multiple_node


class ExtractDate(ExtractionOrder):
    class DateField(Enum):
        YEAR = 'year'
        MONTH = 'month'
        DAY = 'day'

    @property
    def regex(self) -> str:
        return self._regex

    @property
    def date_field_order(self) -> tuple[DateField]:
        return self._date_field_order

    def __init__(self, node_selector: str, target_data: str, regex: str, date_field_order: tuple[DateField]):
        self._node_selector = node_selector
        self._target_data = target_data
        self._multiple_node = False
        if not isinstance(regex, str):
            raise TypeError(f'{regex} is not a string (str) !')
        self._regex = regex
        if not all(date_field in date_field_order for date_field in self.DateField):
            raise ValueError(
                "All DateField must be in date_field_order !"
                + ''.join(['\n - ' + str(date_field) for date_field in self.DateField])
            )
        if len(date_field_order) != 3:
            raise ValueError(
                f"\"date_field_order\" length must be 3 not {len(date_field_order)} !"
            )
        self._date_field_order = date_field_order

    def transform_data(self, data: str) -> date:
        match = re.match(
            self.regex,
            data
        )
        if match:
            matches = match.groups()
            if len(matches) != 3:
                raise ValueError(
                    f"{len(matches)} matches found instead of 3 !\n"
                    f"Check the regex : \"{self.regex}\""
                )
            date_fields = {
                date_field: match
                for date_field, match in zip(self.date_field_order, map(int, matches))
            }
            return date(
                date_fields[self.DateField.YEAR],
                date_fields[self.DateField.MONTH],
                date_fields[self.DateField.DAY]
            )
        else:
            raise ValueError(f"No match found with this regex \"{self.regex}\"")
