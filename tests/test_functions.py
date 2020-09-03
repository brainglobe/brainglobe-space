import numpy as np

import pytest

from bg_space.functions import (
    map_to,
    map_stack_to,
    transformation_matrix_to,
    transform_points_to,
)
from bg_space.core import AnatomicalSpace

valid_origins = ["asl", "ipl", "pls"]


@pytest.mark.parametrize("src_o", valid_origins)
@pytest.mark.parametrize("tgt_o", valid_origins)
def test_function_consistency(src_o, tgt_o):
    shape = (15, 5, 10)
    stack = np.random.rand(*shape)
    assert map_to(src_o, tgt_o) == AnatomicalSpace(src_o, shape).map_to(tgt_o)

    assert np.allclose(
        map_stack_to(src_o, tgt_o, stack),
        AnatomicalSpace(src_o).map_stack_to(tgt_o, stack),
    )

    assert np.allclose(
        transformation_matrix_to(src_o, tgt_o, shape=shape),
        AnatomicalSpace(src_o, shape).transformation_matrix_to(tgt_o),
    )

    pts = np.array([[1, s - 1, s + 1, s * 2 - 1] for s in shape]).T
    assert np.allclose(
        transform_points_to(src_o, tgt_o, pts, shape=shape),
        AnatomicalSpace(src_o, shape).map_points_to(tgt_o, pts),
    )
