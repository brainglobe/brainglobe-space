class SpaceConvention:
    """Class for describing an anatomical 3D space convention.
    Drops the infinitely confusing (x, y, z) for a more semantic specification
    of the ordering and orientation.

    The space is described with an `origin` tuple that specifies
    "to which anatomical direction the 0 of the stack correspond along each
    of the 3 dimensions".

    E.g., in the Allen Brain (http://help.brain-map.org/display/mousebrain/API):
        0. first axis goes from Anterior to posterior;
        1. second axis goes from Dorsal to ventral;
        2. third axis goes from Left to right.

    Therefore, the Allen space can be described with an instance defined in
    any of the following ways:

    >>> SpaceConvention("ADL")
    >>> SpaceConvention(["a", "d", "l"])
    >>> SpaceConvention(["anterior", "dorsal", "left"])

    This can be convenient for quickly reorient a stack to match different
    axes convention.

    Transformations generate with this class ARE NOT proper transformations from
    space a to space b! They are transformations of space a to a new standard
    orientation matching the convention of space B. This can be very useful
    as a pre-step for an affine transformation but does not implement it.

    Parameters
    ----------
    origin : str or tuple of str or list of str
        each letter or initial of each string should match a letter in s
        pace_specs
    shape : tuple, optional
        shape of the bounding box of the space (e.g. shape of a stack)
    """

    # Use sets to avoid any explicit convention definition:
    space_specs = {
        "sagittal": {"p", "a"},
        "vertical": {"d", "v"},
        "frontal": {"l", "r"},
    }

    # Map limits letters to complete names
    lims_labels = {
        "p": "Posterior",
        "a": "Anterior",
        "d": "Dorsal",
        "v": "Ventral",
        "l": "Left",
        "r": "Right",
    }

    def __init__(self, origin, shape=(None, None, None), resolution=(1, 1, 1)):

        # Reformat to lowercase initial:
        origin = [o[0].lower() for o in origin]

        assert all([o in self.lims_labels.keys() for o in origin])

        axs_description = []

        # Loop over origin specification:
        for lim in origin:

            # Loop over possible axes and origin values:
            for k, possible_lims in self.space_specs.items():

                # If origin specification in possible values:
                if lim in possible_lims:
                    # Define orientation string with set leftout element:
                    axs_description.append(
                        ordred_list_from_set(possible_lims, lim)
                    )

        # Makes sure we have a full orientation:
        assert len(axs_description) == 3
        assert len(axs_description) == len(set(axs_description))

        # Univoke description of the space convention with a tuple of axes lims:
        self.axs_description = tuple(axs_description)

        self.shape = shape
        self.resolution = resolution

    @property
    def axs_order(self):
        """
        Returns
        -------
        tuple
            Tuple of  `self.space_specs` keys specifying axes order
        """
        order = []
        for lims in self.axs_description:
            order += [
                k for k, val in self.space_specs.items() if lims[0] in val
            ]

        return tuple(order)

    @property
    def origin(self):
        """
        Returns
        -------
        tuple
            Three letters specifying origin position.
        """
        return tuple([l[0] for l in self.axs_description])


def ordred_list_from_set(input_set, first):
    """
    Parameters
    ----------
    input_set : set
        2-elements set
    first :
        first element for the output list

    Returns
    -------

    """
    return first + next(iter(input_set - {first}))
