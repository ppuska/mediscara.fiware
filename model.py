"""Module for storing data about the production models"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, List

logger = logging.getLogger("django")


@dataclass
class ProductionOrder(ABC):
    """Abstract base class to represend Procuction Orders"""

    type: ClassVar[str] = "order"

    created: str = field(init=False)
    active: bool = field(default=False)

    def __post_init__(self):
        self.created = datetime.now().strftime("%y.%m.%d %H:%M:%S")

    @abstractmethod
    def to_ngsi(self) -> dict:
        """Converts the class to its NGSi v2 formatted dict representation"""
        return {
            "type": self.type,
            "value": {
                "created": {"type": "Text", "value": self.created},
                "active": {"type": "Bool", "value": self.active},
            },
        }

    @classmethod
    @abstractmethod
    def from_ngsi(cls, entity: dict):
        """Attempts to create a container from the NGSi v2 data"""
        order = cls()

        try:
            order.created = entity["value"]["created"]["value"]
            order.active = entity["value"]["active"]["value"]

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
    count: int = field(default=0)

    def to_ngsi(self) -> dict:
        ngsi_dict = super().to_ngsi()
        ngsi_dict["value"]["incubator_type"] = {
            "type": self.ngsi_type(self.incubator_type),
            "value": self.incubator_type,
        }
        ngsi_dict["value"]["count"] = {"type": self.ngsi_type(self.count), "value": self.count}
        return ngsi_dict

    @classmethod
    def from_ngsi(cls, entity: dict):

        try:
            order = super().from_ngsi(entity=entity)
            order.incubator_type = str(entity["value"]["incubator_type"]["value"])
            order.count = int(entity["value"]["count"]["value"])

        except KeyError as error:
            logger.warning("Errors in incoming JSON object: %s", str(entity))
            raise KeyError from error

        return order


@dataclass
class IndustialOrder(ProductionOrder):
    """Data class to represent the Industrial cell production orders"""

    type = f"{ProductionOrder.type}.industrial"

    incubator_type: str = field(default="")
    count: int = field(default=0)

    def to_ngsi(self) -> dict:
        return {
            "type": self.type,
            "value": {
                "incubator_type": {"type": self.ngsi_type(self.incubator_type), "value": self.incubator_type},
                "count": {"type": self.ngsi_type(self.count), "value": self.count},
            },
        }

    @classmethod
    def from_ngsi(cls, entity: dict):
        order = cls()
        try:
            order.incubator_type = str(entity["value"]["incubator_type"]["value"])
            order.count = int(entity["value"]["count"]["value"])

        except KeyError as error:
            logger.warning("Errors in incoming JSON object: %s", str(entity))
            raise KeyError from error

        return order


@dataclass
class Container:
    """Data class to contain the list of orders"""

    order_list: List[ProductionOrder] = field(default_factory=list)

    type: str = field(init=False)

    def __post_init__(self):
        if self.order_list:  # list is not empty
            self.type = f"{self.order_list[0].type}.container"

        else:
            self.type = "container"

    def to_ngsi(self):
        """Converts the class to its NGSi v2 formatted dict representation"""
        result = {}
        result["id"] = self.type

        result["type"] = self.type

        result["order_list"] = {"type": "StructuredValue", "value": []}

        for item in self.order_list:
            result["order_list"]["value"].append(item.to_ngsi())

        return result

    @classmethod
    def from_ngsi(cls, entity: dict):
        """Attempts to create a container from the NGSi v2 data
        Args:
            entity (dict): The entity as a NGSi v2 formatted dict
        Returns:
            Container: The created container
        Raises:
            KeyError: if the incoming JSON buffer can not be properly parsed
        """
        container = cls()

        try:
            container.type = entity["type"]  # get the type
            order_list = entity["order_list"]["value"]

        except KeyError as error:
            logger.warning("Unable to create entity, errors were found in the incoming JSON object")
            raise KeyError from error

        for item in order_list:

            try:
                item_type = item["type"]

            except KeyError as error:
                logger.warning("Errors found in incoming JSON object: %s", str(item))
                raise KeyError from error

            if item_type == CollaborativeOrder.type:
                container.order_list.append(CollaborativeOrder.from_ngsi(item))

            elif item_type == IndustialOrder.type:
                container.order_list.append(IndustialOrder.from_ngsi(item))

            else:
                raise KeyError(f"Invalid item type: {item_type}")

        return container

    @staticmethod
    def get_industrial_id():
        """Returns the ID of an industrial order container"""
        return f"{IndustialOrder.type}.container"

    @staticmethod
    def get_collaborative_id():
        """Returns the ID of a collaborative order container"""
        return f"{CollaborativeOrder.type}.container"

    @property
    def container_id(self):
        """Returns the id of the container"""
        return self.type
