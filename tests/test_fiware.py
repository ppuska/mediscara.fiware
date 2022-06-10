"""Module for testing the fiware connector"""

import sys
import pytest

from ..fiware import FIWARE

OCB_URL = 'http://localhost:1026'

@pytest.fixture
def connector():
    return FIWARE(server_url=OCB_URL)