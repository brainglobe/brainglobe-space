import numpy as np

from brainglobe_space import AnatomicalSpace


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
        array with elements describing an anatomical location
        (e.g. "als", "pir)

    """
    space = AnatomicalSpace(origin)
    arrays = []
    for lims, hs in zip(space.axes_description, half_shape):
        arrays.append(
            np.array(
                [
                    lims[0],
                ]
                * hs
                + [
                    lims[1],
                ]
                * hs
            )
        )

    x, y, z = np.meshgrid(*arrays, indexing="ij")

    return np.char.add(np.char.add(x, y), z)
