import pytest


@pytest.fixture
def valid_origins():
    return ["asl", "sla", "ipl", "rai", "las", "pli"]


@pytest.fixture
def some_shapes():
    return [(3, 3, 3), (15, 5, 10)]
