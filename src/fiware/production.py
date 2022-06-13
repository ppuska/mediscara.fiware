"""Module for the managerial production messages"""

from typing import List, Type

from .fiware import FIWARE
from .model import ProductionOrder


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
        return self.__fiware.create_entity(order.to_ngsi())

    def load_production_orders(self, order: Type[ProductionOrder]) -> List[ProductionOrder]:

        entities = self.__fiware.get_entities_with_type(order.type)

        if entities is None:
            return []

        orders = []

        for entity in entities:
            orders.append(order.from_ngsi(entity))

        return orders

    def delete_production_order(self, order: ProductionOrder) -> bool:

        return self.__fiware.delete_entity(order.id)

    def update_production_order_remaining(self, new_order: ProductionOrder):
        """Updates the production remaining attribute of the given order, to the order's new value"""

        return self.__fiware.update_entity_attribute(new_order.id, attr="remaining", value=str(new_order.remaining))

    def set_active(self, order: ProductionOrder, active: bool):
        """Sets the active value of the order in the OCB to the given value"""

        assert isinstance(str(active), str)

        return self.__fiware.update_entity_attribute(entity_id=order.id, attr="active", value=str(active))
