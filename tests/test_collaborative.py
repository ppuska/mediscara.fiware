"""Module for testing the Collaborative orders"""

import pytest

from fiware.production import Production
from fiware.model import CollaborativeOrder

OCB_URL = 'http://localhost:1026'

@pytest.fixture
def connector():
    return Production(server_url=OCB_URL)

def test_create_read_delete(connector):
    assert isinstance(connector, Production)

    order = CollaborativeOrder(incubator_type='type1',
                               part_type='part1',
                               count=10
                               )

    assert connector.new_production_order(order) is True

    assert connector.load_production_orders(order=CollaborativeOrder) is not None

    assert connector.update_production_order_remaining(order) is True

    assert connector.set_active(order=order, active=True) is True

    assert connector.delete_production_order(order=order) is True