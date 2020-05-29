import pytest
import numpy as np
import itertools

from bgspace import SpaceConvention

char_add = np.core.defchararray.add


def create_label_array(origin, half_shape):
    """Create stack with string labels marking regions for testing
    Parameters
    ----------
    origin : str
        Valid origin for a SpaceConvention obj.
    half_shape : tuple
        Half shape of the stack on each axis.

    Returns
    -------
    np.array of chars
        array with elements describing an anatomical location (e.g. "als", "pir)

    """
    space = SpaceConvention(origin)
    arrays = []
    for lims, hs in zip(space.axes_description, half_shape):
        arrays.append(np.array([lims[0],] * hs + [lims[1],] * hs))

    x, y, z = np.meshgrid(*arrays, indexing="ij")

    return char_add(char_add(x, y), z)


@pytest.mark.parametrize(
    "origin",
    [
        "rsa",
        ["r", "s", "a"],
        ("R", "S", "A"),
        ("rl", "si", "ap"),
        ["right", "superior", "anterior"],
    ],
)
def test_origin_types(origin):
    space = SpaceConvention(origin)
    assert space.axes_description == ("rl", "si", "ap")


@pytest.mark.parametrize(
    "origin, errortype",
    [
        ("rvu", AssertionError),
        ("rra", AssertionError),
        ("rsaa", AssertionError),
        (("r", "s", 1), TypeError),
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
        ("ars", ("sagittal", "frontal", "vertical"), ("a", "r", "s")),
        ("sar", ("vertical", "sagittal", "frontal"), ("s", "a", "r")),
        ("lip", ("frontal", "vertical", "sagittal"), ("l", "i", "p")),
        ("ila", ("vertical", "frontal", "sagittal"), ("i", "l", "a")),
    ],
)
def test_properties(o, axs_order, origin):
    space = SpaceConvention(o)
    assert space.axes_order == axs_order
    assert space.origin == origin


# define some conditions to be cross_checked:
def test_stack_flips(valid_origins, some_shapes):

    for (src_o, tgt_o, src_shape, tgt_shape) in itertools.product(
        valid_origins, valid_origins, some_shapes, some_shapes
    ):
        source_stack = create_label_array(src_o, src_shape)
        target_stack = create_label_array(tgt_o, tgt_shape)

        source_space = SpaceConvention(src_o)
        target_space = SpaceConvention(tgt_o)

        # Check all corners of the mapped stack:
        mapped_stack = source_space.map_stack_to(source_stack, target_space)
        for indexes in itertools.product([0, -1], repeat=3):
            assert set(mapped_stack[indexes]) == set(target_stack[indexes])
