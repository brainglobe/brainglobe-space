import pytest

from bgspace import SpaceConvention


@pytest.mark.parametrize(
    "origin",
    [
        "rda",
        ["r", "d", "a"],
        ("R", "D", "A"),
        ("rl", "dv", "ap"),
        ["right", "dorsal", "anterior"],
    ],
)
def test_origin_types(origin):
    space = SpaceConvention(origin)
    assert space.axs_description == ("rl", "dv", "ap")


@pytest.mark.parametrize(
    "origin, errortype",
    [
        ("rvu", AssertionError),
        ("rra", AssertionError),
        ("rdaa", AssertionError),
        (("r", "d", 1), TypeError),
        ((1, 2, 3), TypeError),
    ],
)
def test_init_failures(origin, errortype):
    with pytest.raises(errortype) as error:
        _ = SpaceConvention(origin)
    assert str(errortype).split("'")[1] in str(error)


@pytest.mark.parametrize(
    "o, axs_order, origin",
    [
        ("ard", ("sagittal", "frontal", "vertical"), ("a", "r", "d")),
        ("dar", ("vertical", "sagittal", "frontal"), ("d", "a", "r")),
        ("lvp", ("frontal", "vertical", "sagittal"), ("l", "v", "p")),
        ("vla", ("vertical", "frontal", "sagittal"), ("v", "l", "a")),
    ],
)
def test_properties(o, axs_order, origin):
    space = SpaceConvention(origin)
    assert space.axs_order == axs_order
    assert space.origin == origin
