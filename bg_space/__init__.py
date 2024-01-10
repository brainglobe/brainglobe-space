from warnings import warn

warn(
    "bg-space has been retired from the BrainGlobe tool suite and replaced by brainglobe-space. We recommend you uninstall this package and install brainglobe-space instead: https://github.com/brainglobe/brainglobe-space",
    DeprecationWarning,
)

__author__ = """Luigi Petrucco @brainglobe"""
__version__ = "0.6.0"

from bg_space.core import AnatomicalSpace, SpaceConvention
from bg_space.functions import (
    map_to,
    map_stack_to,
    transformation_matrix_to,
    transform_points_to,
)
