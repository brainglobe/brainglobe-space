import pytest


@pytest.fixture
def valid_origins():
    return ["asl", "sla", "ipl", "rai", "las", "pli"]


@pytest.fixture
def some_shapes():
    return [(1, 1, 1), (15, 5, 10)]
