"""Module for storing interface classes"""

from email import header
import logging
from enum import Enum

import requests


class StatusCodes(Enum):
    """Enum class to store the HTTP request response status codes"""

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    NOT_FOUND = 404
    UNPROCESSABLE = 422


class FIWARE:
    """Communication class for interfacing with the Orion Context Broker"""

    def __init__(self, server_url: str) -> bool:
        """Initializes the communication to the FIWARE OCB
        Args:
            server_addr (str): The IPv4 address of the OCB server
        Raises:
            ConnectionError: If the connection cannot be established
        """
        self.__server_url = server_url

        # test the connection to the server
        try:
            response = requests.get(f"{self.__server_url}/v2")

            if response.status_code == StatusCodes.OK.value:
                logging.info("Communication initialized, server online")

            else:
                logging.info("Communication initalized, server unreachable (response %i)", response.status_code)

        except requests.exceptions.ConnectionError as error:
            logging.error("Failed to establish connection")
            raise ConnectionError from error

    def create_entity(self, entity: dict) -> bool:
        """Creates an entity in the OCB
        Args:
            entity (dict): The JSON representation formatted as NGSIv2
        Returns:
            bool: Whether the operation was successful or not
        """

        response = requests.post(f"{self.__server_url}/v2/entities", json=entity)

        if response.status_code == StatusCodes.CREATED.value:
            return True

        logging.info("Could not create new entity '%s' (response: %s)", entity, response.content)
        return False

    def get_entity(self, entity_id: str) -> dict or None:
        """Return the entity with the given id from the OCB
        Args:
            entity_id (str): The id of the entity
        Returns:
            dict or None: The JSON representation of the entity, or None if the entity was not found
        """

        response = requests.get(f"{self.__server_url}/v2/entities/{entity_id}")

        if response.status_code == StatusCodes.NOT_FOUND.value:
            logging.debug("%s not found.", entity_id)
            return None

        return response.json()

    def get_entities_with_type(self, entity_type: str):
        """Lists all the entities with the given type"""

        params = {
            'type': entity_type
        }

        response = requests.get(f"{self.__server_url}/v2/entities", params=params)

        return response.json()



    def update_entity(self, entity_id: str, attrs: dict) -> bool:
        """Updates the entity with the given id in the OCB
        Args:
            entity_id (str): The ID of the entity
            attrs (dict): the attributes of the entity to be updated
        Returns:
            bool: Whether the operation was successful
        """
        response = requests.patch(f"{self.__server_url}/v2/entities/{entity_id}/attrs", json=attrs)

        if response.status_code == StatusCodes.NO_CONTENT.value:
            return True

        logging.info("Unable to update entity '%s'. (response %s)", entity_id, response.content)
        return False

    def update_entity_attribute(self, entity_id: str, attr: str, value: str):
        """Updates the selected attribute in the entity with the given id"""

        headers = {
            "Content-Type": 'text/plain',
        }

        assert isinstance(value, str)

        response = requests.put(f"{self.__server_url}/v2/entities/{entity_id}/attrs/{attr}/value",
                                headers=headers,
                                data=value
                                )

        if response.status_code == StatusCodes.NO_CONTENT.value:
            return True

        logging.info("Unable to update attribute '%s' of entity '%s'. (response %s)", attr, entity_id, response.content)
        return False

    def replace_entity(self, entity: dict) -> bool:
        """Replaces the entity with the given data"""

        data = {"actionType": "REPLACE", "entities": [entity]}

        response = requests.post(f"{self.__server_url}/v2/op/update", json=data)

        if response.status_code == StatusCodes.NO_CONTENT.value:
            return True

        return False

    def update_entity_append(self, entity: dict):
        """Attempts to update the entity using the append update action
        Args:
            entity (dict): The entity formatted as NGSi v2 data
        Returns:
            bool: Whether the operation was successful
        """

        payload = {"actionType": "append", "entities": []}

        payload["entities"].append(entity)

        response = requests.post(f"{self.__server_url}/v2/op/update", json=payload)

        if response.status_code == StatusCodes.NO_CONTENT.value:
            return True

        logging.info("Unable to update entity. (response %s)", response.content)
        return False

    def delete_entity(self, entity_id: str):
        """Deletes the entity from the OCB
        Args:
            entity_id (str): The ID of the entity
        Returns:
            _type_: Whether the operation was successful or not
        """
        response = requests.delete(f"{self.__server_url}/v2/entities/{entity_id}")

        if response.status_code == StatusCodes.NO_CONTENT.value:
            return True

        logging.info("Unable to delete entity '%s'. (response %s'", entity_id, response.content)
        return False
