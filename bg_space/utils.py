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
