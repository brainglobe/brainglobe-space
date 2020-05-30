import itertools
import numpy as np

import pytest

from .utils import create_label_array
from bgspace import SpaceConvention

valid_origins = ["asl", "ipl", "pli"]
some_shapes = [(3, 3, 3), (15, 5, 10)]


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


@pytest.mark.parametrize("valid_origins", ["asl", "sla", "pir"])
# @pytest.mark.parametrize("target_args, shape", [("asl"), (1, 2, 3)])
def test_shape_decorator(valid_origins):
    correct_shape = (20, 30, 10)
    origin = "asl"
    source_space = SpaceConvention(origin, correct_shape)

    target_space = SpaceConvention(origin, correct_shape)
    correct_mat = source_space.transformation_matrix_to(target_space)

    # Check if we can overwrite none or different orientations:
    for args in [(origin, None), (origin, correct_shape[::-1])]:
        new_shape_mat = SpaceConvention(*args).transformation_matrix_to(
            target_space, shape=correct_shape
        )

        assert np.allclose(correct_mat, new_shape_mat)


# define some conditions to be cross_checked:
@pytest.mark.parametrize("src_o", valid_origins)
@pytest.mark.parametrize("tgt_o", valid_origins)
@pytest.mark.parametrize("src_shape", some_shapes)
@pytest.mark.parametrize("tgt_shape", some_shapes)
def test_stack_flips(src_o, tgt_o, src_shape, tgt_shape):
    source_stack = create_label_array(src_o, src_shape)
    target_stack = create_label_array(tgt_o, tgt_shape)

    source_space = SpaceConvention(src_o)

    # Test both mapping to SpaceConvention obj and origin with decorator:
    for target_space in [tgt_o, SpaceConvention(tgt_o)]:
        # Check all corners of the mapped stack:
        mapped_stack = source_space.map_stack_to(target_space, source_stack)
        for indexes in itertools.product([0, -1], repeat=3):
            assert set(mapped_stack[indexes]) == set(target_stack[indexes])


# define some conditions to be cross_checked:
@pytest.mark.parametrize("src_o", valid_origins)
@pytest.mark.parametrize("tgt_o", valid_origins)
@pytest.mark.parametrize("src_shape", some_shapes)
@pytest.mark.parametrize("tgt_shape", some_shapes)
def test_point_transform(src_o, tgt_o, src_shape, tgt_shape):
    # Create an array with descriptive space labels:
    source_stack = create_label_array(src_o, src_shape)

    # Create spaces objects:
    source_space = SpaceConvention(src_o, shape=[s * 2 for s in src_shape])

    # Test both mapping to SpaceConvention obj and origin with decorator:
    for target_space in [tgt_o, SpaceConvention(tgt_o)]:

        # Define grid of points sampling 4 points per axis:
        grid_positions = [[1, s - 1, s + 1, s * 2 - 1] for s in src_shape]
        source_pts = np.array(list(itertools.product(*grid_positions)))

        # Map points and stack to target space:
        mapped_pts = source_space.map_points_to(target_space, source_pts)
        mapped_stack = source_space.map_stack_to(target_space, source_stack)

        # Check that point coordinates keep the same values:
        for p_source, p_mapped in zip(source_pts, mapped_pts):
            p_s, p_m = [tuple(p.astype(np.int)) for p in [p_source, p_mapped]]

            assert source_stack[p_s] == mapped_stack[p_m]
