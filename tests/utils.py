import numpy as np

from bg_space import AnatomicalSpace

char_add = np.core.defchararray.add


def create_label_array(origin, half_shape):
    """Create stack with string labels marking regions for testing.

    Parameters
    ----------
    origin : str
        Valid origin for a AnatomicalSpace obj.
    half_shape : tuple
        Half shape of the stack on each axis.

    Returns
    -------
    np.array of chars
        array with elements describing an anatomical location (e.g. "als", "pir)

    """
    space = AnatomicalSpace(origin)
    arrays = []
    for lims, hs in zip(space.axes_description, half_shape):
        arrays.append(np.array([lims[0],] * hs + [lims[1],] * hs))

    x, y, z = np.meshgrid(*arrays, indexing="ij")

    return char_add(char_add(x, y), z)
