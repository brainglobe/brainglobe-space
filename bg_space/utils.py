import functools
import warnings


def ordered_list_from_set(input_set, first):
    """
    Parameters
    ----------
    input_set : set
        2-elements set
    first :
        First element for the output list

    Returns
    -------

    """
    return first + next(iter(input_set - {first}))


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    def decorator(func1):
        @functools.wraps(func1)
        def new_func1(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(reason, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)
            return func1(*args, **kwargs)

        return new_func1

    return decorator
