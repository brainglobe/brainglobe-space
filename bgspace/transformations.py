import numpy as np


def map_axs_from_a_to_b(a, b):
    """Find axes reordering and flips required to go
    from SpaceConvention a to SpaceConvention b.

    Note::
        the flips order is defined in b SpaceConvention order of axes! So,
        when using this mapping, first change the order and then flip.

    Parameters
    ----------
    a : SpaceConvention
        moving space convention
    b : SpaceConvention
        target space convention

    Returns
    -------
    tuple
        axes order to move from space a to space b
    tuple
        sequence of clips moving from space a to space b (in b axis order)

    """

    # Get order of matching axes:
    order = tuple([a.axs_order.index(ax) for ax in b.axs_order])

    # Detect required flips:
    flips = tuple(
        [
            a.axs_description[ai] != b.axs_description[bi]
            for bi, ai in enumerate(order)
        ]
    )

    return order, flips


def move_stack_from_a_to_b(stack, a, b, copy=False):
    """ Transpose and flip stack to go from space a to space b. This is NOT
    a transformation from space a to space b: the output will be in space
    a, described with a different axis convention.
    Parameters
    ----------
    stack : numpy array
        stack to port from space convention a to space convention b
    a : SpaceConvention
        moving space convention
    b : SpaceConvention
        target space convention
    copy : bool, optional

    Returns
    -------

    """
    # Find order swapping and flips:
    order, flips = map_axs_from_a_to_b(a, b)

    # If we want to work on a copy, create:
    if copy:
        stack = stack.copy()

    # Transpose axes:
    stack = stack.transpose(*order)

    # Flip as required:
    stack = np.flip(stack, [i for i, f in enumerate(flips) if f])

    return stack


def trasfmatrix_from_a_to_b(a, b):
    """ Find transformation matrix going from SpaceConvention a to SpaceConvention b.

    This is not in general a proper affine transformation from space a to space b, as
    this is the case only if spaces a and b have the same shape and resolution.
    This function is only supposed to provide a easy transformation to move
    coordinates along with a stack orientation.


    Parameters
    ----------
    a
    b

    Returns
    -------

    """
    # Find axorder swapping and flips:
    order, flips = map_axs_from_a_to_b(a, b)

    mat = np.zeros((4, 4))
    mat[-1, -1] = 1
    for ai, (bi, f) in enumerate(zip(order, flips)):
        mat[ai, bi] = -1 if f else 1

        mat[ai, 3] = a.shape[ai] if f else 0
