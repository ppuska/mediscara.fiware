"""Module for the managerial production messages"""

import logging
from enum import Enum

from . import ENTITY_ID
from .fiware import FIWARE
from .model import Container, ProductionOrder


class DESTINATION(Enum):
    """Enum clas to store the porrible message destinations"""

    ROBOTIC = f"{ENTITY_ID}.robotic"
    COLLABORATIVE = f"{ENTITY_ID}.collaborative"


class Production:
    """Class for generating production messages to the FIWARE Orion Context Broker"""

    def __init__(self, server_url: str) -> None:
        """Initializes the Production class
        Args:
            server_address (str): The IPv4 address of the server
        Raises:
            ConnectionError: If the FIWARE connector is unable to connect to the broker
        """

        self.__fiware = FIWARE(server_url=server_url)

    def new_production_order(self, order: ProductionOrder) -> bool:
        """Creates a new production order and attempts to upload it to the OCB
        Returns:
            bool: Whether the operation was successful or not
        """
        # First check if the entity's container already exists
        container = Container(order_list=[order])

        ocb_container_entity = self.__fiware.get_entity(entity_id=container.container_id)

        if ocb_container_entity is None:
            # If the container does not exist in the OCB create it
            logging.info("Container does not exist, creating it...")
            return self.__fiware.create_entity(entity=container.to_ngsi())

        # the container exists in the ocb
        container = Container.from_ngsi(ocb_container_entity)

        # append the new order to the container
        container.order_list.append(order)

        return self.__fiware.update_entity_append(container.to_ngsi())

    def load_production_orders(self, container_id: str) -> Container:

        entity = self.__fiware.get_entity(entity_id=container_id)

        if entity is None:
            container = Container()
            container.type = container_id
            return container

        return Container.from_ngsi(entity)

    def delete_production_order(self, container_id: str, created: str) -> bool:

        entity = self.__fiware.get_entity(entity_id=container_id)

        order_list = entity["order_list"]["value"]
        new_order_list = order_list

        assert isinstance(order_list, list)

        print(new_order_list)

        for order in order_list:
            print(order["value"]["created"]["value"], created, order["value"]["created"]["value"] == created)
            if order["value"]["created"]["value"] == created:
                new_order_list.remove(order)  # remove the given order

        print(new_order_list)
        entity["order_list"]["value"] = new_order_list  # write back the updated order list

        return self.__fiware.replace_entity(entity=entity)  # replace the updated entity
