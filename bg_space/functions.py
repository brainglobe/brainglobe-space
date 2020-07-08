from bg_space.core import SpaceConvention


# TODO convert to a smarter way to generate those parsing class' methods:
def map_to(source, target):
    """Find axes reordering and flips required to go to
    target space convention.

    Parameters
    ----------
    source :
        Source space origin.
    target : str
        Target space origin.

    Returns
    -------
    tuple
        Axes order to move to target space.
    tuple
        Sequence of flips to move to target space (in target axis order).

        """
    return SpaceConvention(source).map_to(target)


def map_stack_to(source, target, stack, copy=False):
    """Transpose and flip stack to move it to target space convention.

    Parameters
    ----------
    source : str or tuple or list
        Source space origin.
    target : str or tuple or list
        Target space origin.
    stack : numpy array
        Stack to map from space convention a to space convention b
    copy : bool, optional
        If true, stack is copied.

    Returns
    -------

    """
    return SpaceConvention(source).map_stack_to(target, stack, copy=False)


def transformation_matrix_to(source, target, shape=None):
    """Find transformation matrix going to target space convention.

    Parameters
    ----------
    source : str or tuple or list
        Source space origin.
    target : str or tuple or list
        Target space origin.
    shape : tuple, optional
        Must be passed if flips are required.

    Returns
    -------

    """
    return SpaceConvention(source, shape).transformation_matrix_to(target)


def transform_points_to(source, target, points, shape=None):
    """Map points to target space convention.

    Parameters
    ----------
    source : str or tuple or list
        Source space origin.
    target : str or tuple or list
        Target space origin.
    pts : (n, 3) numpy array
        Array with the points to be mapped.
    shape : tuple, optional
        Must be passed if flips are required.

    Returns
    -------
    (n, 3) numpy array
        Array with the transformed points.
    """
    return SpaceConvention(source, shape).map_points_to(target, points)
