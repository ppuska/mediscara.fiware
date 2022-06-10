

import pytest

from fiware.fiware import FIWARE

OCB_URL = "http://localhost:1026"

@pytest.fixture
def connector():
    return FIWARE(server_url=OCB_URL)


def test_get(connector):
    assert isinstance(connector, FIWARE)

    assert connector.get_entities_with_type('order.collaborative') is not None