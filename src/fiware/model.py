"""Module for storing data about the production models"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

logger = logging.getLogger("django")


@dataclass
class ProductionOrder(ABC):
    """Abstract base class to represend Procuction Orders"""

    type: ClassVar[str] = "order"

    id: str = field(init=False)  # pylint:disable=invalid-name

    active: bool = field(default=False)

    count: int = field(default=1)
    remaining: int = field(init=False)

    def __post_init__(self):
        self.id = f'{self.type}:{datetime.now().strftime("%y_%m_%d_%H_%M_%S")}'
        self.remaining = self.count

    @abstractmethod
    def to_ngsi(self) -> dict:
        """Converts the class to its NGSi v2 formatted dict representation"""
        return {
            "id": self.id,
            "type": self.type,
            "active": {"type": self.ngsi_type(self.active), "value": self.active},
            "count": {"type": self.ngsi_type(self.count), "value": self.count},
            "remaining": {"type": self.ngsi_type(self.remaining), "value": self.remaining},
        }

    @classmethod
    @abstractmethod
    def from_ngsi(cls, entity: dict):
        """Attempts to create a container from the NGSi v2 data"""
        order = cls()

        try:
            order.id = entity["id"]
            order.type = entity["type"]
            order.active = entity["active"]["value"]
            order.count = entity["count"]["value"]
            order.remaining = entity["remaining"]["value"]

        except KeyError as error:
            logger.warning("Errors in incoming JSON object: %s", str(entity))
            raise KeyError from error

        return order

    @staticmethod
    def ngsi_type(attribute) -> str:
        """Attempts to map the objects native python type to the NGSi v2 types
        Args:
            attribute (object): The attribute of the dataclass
        Returns:
            str: the type of the object as a string
        Raises:
            ValueError: if the type cannot be converted
        """

        if isinstance(attribute, str):
            return "Text"

        if isinstance(attribute, (int, float)):
            return "Number"

        if isinstance(attribute, bool):
            return "Boolean"

        raise ValueError(f"Cannot convert type of {type(attribute)} to a NGSi v2 type")


@dataclass
class CollaborativeOrder(ProductionOrder):
    """Data class to represent the Collaborative cell production orders"""

    type = f"{ProductionOrder.type}.collaborative"

    incubator_type: str = field(default="")
    part_type: str = field(default="")

    def to_ngsi(self) -> dict:
        ngsi_dict = super().to_ngsi()
        ngsi_dict["incubator_type"] = {
            "type": self.ngsi_type(self.incubator_type),
            "value": self.incubator_type,
        }
        ngsi_dict["part_type"] = {
            'type': self.ngsi_type(self.part_type),
            'value': self.part_type
        }
        return ngsi_dict

    @classmethod
    def from_ngsi(cls, entity: dict):

        try:
            order = super().from_ngsi(entity=entity)
            order.incubator_type = str(entity["incubator_type"]["value"])
            order.part_type = str(entity["part_type"]['value'])

        except KeyError as error:
            logger.warning("Errors in incoming JSON object: %s", str(entity))
            raise KeyError from error

        return order


@dataclass
class IndustialOrder(ProductionOrder):
    """Data class to represent the Industrial cell production orders"""

    type = f"{ProductionOrder.type}.industrial"

    housing_type: str = field(default="")
    count: int = field(default=0)

    def to_ngsi(self) -> dict:
        ngsi_dict = super().to_ngsi()
        ngsi_dict['type'] = self.type
        ngsi_dict['housing_type'] = {"type": self.ngsi_type(self.housing_type), "value": self.housing_type}

        return ngsi_dict

    @classmethod
    def from_ngsi(cls, entity: dict):
        try:
            order = super().from_ngsi(entity=entity)
            order.housing_type = str(entity["housing_type"]["value"])

        except KeyError as error:
            logger.warning("Errors in incoming JSON object: %s", str(entity))
            raise KeyError from error

        return order
