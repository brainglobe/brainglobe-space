import numpy as np
from bgspace.utils import ordered_list_from_set


def to_target(method):
    """Decorator for bypassing SpaceConvention creation.
    """

    def decorated(spaceconv_instance, space_description, *args, **kwargs):

        # isinstance(..., SpaceConvention) here would fail, so:
        if not type(space_description) == type(spaceconv_instance):
            # Generate description if input was not:
            space_description = SpaceConvention(space_description)

        return method(spaceconv_instance, space_description, *args, **kwargs)

    return decorated


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
        Each letter or initial of each string should match a letter in s
        pace_specs
    shape : tuple, optional
        Shape of the bounding box of the space (e.g. shape of a stack)
    """

    # Use sets to avoid any explicit convention definition:
    space_specs = {
        "sagittal": {"p", "a"},
        "vertical": {"s", "i"},
        "frontal": {"l", "r"},
    }

    map_planes_from_axes = {
        "sagittal": {"p", "a", "s", "i"},
        "frontal": {"s", "i", "l", "r"},
        "horizontal": {"p", "a", "l", "r"},
    }

    # Map limits letters to complete names
    lims_labels = {
        "p": "posterior",
        "a": "anterior",
        "s": "superior",
        "i": "inferior",
        "l": "left",
        "r": "right",
    }

    def __init__(self, origin, shape=None):

        self.shape = shape

        # Reformat to lowercase initial:
        origin = [o[0].lower() for o in origin]

        axs_description = []

        # Loop over origin specification:
        for lim in origin:

            # Loop over possible axes and origin values:
            for k, possible_lims in self.space_specs.items():

                # If origin specification in possible values:
                if lim in possible_lims:
                    # Define orientation string with set leftout element:
                    axs_description.append(
                        ordered_list_from_set(possible_lims, lim)
                    )

        # Makes sure we have a full orientation:
        assert len(axs_description) == 3
        assert len(axs_description) == len(set(axs_description))

        # Univoke description of the space convention with a tuple of axes lims:
        self.axes_description = tuple(axs_description)

    @property
    def axes_order(self):
        """
        Returns
        -------
        tuple
            `self.space_specs` keys specifying axes order.
        """
        order = []
        for lims in self.axes_description:
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
        return tuple([lim[0] for lim in self.axes_description])

    @to_target
    def map_to(self, target):
        """Find axes reordering and flips required to go to
        target space convention.

        Parameters
        ----------
        target : SpaceConvention object or valid origin
            Target space convention.

        Returns
        -------
        tuple
            Axes order to move to target space.
        tuple
            Sequence of flips to move to target space (in target axis order).

        """

        # Get order of matching axes:
        order = tuple([self.axes_order.index(ax) for ax in target.axes_order])

        # Detect required flips:
        flips = tuple(
            [
                self.axes_description[si] != target.axes_description[ti]
                for ti, si in enumerate(order)
            ]
        )

        return order, flips

    @to_target
    def map_stack_to(self, target, stack, copy=False):
        """Transpose and flip stack to move it to target space convention.

        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.
        stack : numpy array
            Stack to map from space convention a to space convention b
        copy : bool, optional
            If true, stack is copied.

        Returns
        -------

        """

        # Find order swapping and flips:
        order, flips = self.map_to(target)

        # If we want to work on a copy, create:
        if copy:
            stack = stack.copy()

        # Transpose axes:
        stack = np.transpose(stack, order)

        # Flip as required:
        stack = np.flip(stack, [i for i, f in enumerate(flips) if f])

        return stack

    @to_target
    def transformation_matrix_to(self, target, shape=None):
        """Find transformation matrix going to target space convention.

        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.
        shape : tuple, opt
            Must be passed if the object does not have one specified.

        Returns
        -------

        """
        shape = shape if shape is not None else self.shape

        # Find axes order and flips:
        order, flips = self.map_to(target)

        # Instantiate transformation matrix:
        transformation_mat = np.zeros((4, 4))
        transformation_mat[-1, -1] = 1

        # Fill it in the required places:
        for ai, (bi, f) in enumerate(zip(order, flips)):
            # Add the ones for the flips and swaps:
            transformation_mat[ai, bi] = -1 if f else 1

            # If flipping is necessary, we also need to translate origin:
            if shape is None:
                raise TypeError(
                    "A valid shape is required for this transformation!"
                )
            origin_offset = shape[bi] if f else 0

            transformation_mat[ai, 3] = origin_offset

        return transformation_mat

    @to_target
    def map_points_to(self, target, pts, shape=None):
        """Map points to target space convention.
        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.
        pts : (n, 3) numpy array
            Array with the points to be mapped.
        shape : tuple, opt
            Must be passed if the object does not have one specified.

        Returns
        -------
        (n, 3) numpy array
            Array with the transformed points.
        """
        shape = shape if shape is not None else self.shape

        transformation_mat = self.transformation_matrix_to(target, shape=shape)

        # A column of zeros is required for the matrix multiplication:
        pts_to_transform = np.insert(pts, 3, np.ones(pts.shape[0]), axis=1)

        return (transformation_mat @ pts_to_transform.T).T[:, :3]

    @property
    def index_pairs(self):
        """Tuple of index pairs for the remaining axes for projections
        Returns
        -------
        tuple of tuples
            index tuples
        """
        pairs = []
        for i in range(3):
            indexes = list(np.arange(3))
            indexes.pop(i)
            pairs.append(tuple(indexes))

        return tuple(pairs)

    @property
    def sections(self):
        """Return ordered sections names.
        
        Returns
        -------
        tuple of str
            Tuple with the section names

        """
        planes = []
        for idx0, idx1 in self.index_pairs:
            ax0, ax1 = self.axes_description[idx0], self.axes_description[idx1]
            for k, vals in self.map_planes_from_axes.items():
                if ax0[0] in vals and ax1[0] in vals:
                    planes.append(k)

        return tuple(planes)

    @property
    def axis_labels(self):
        """Get axis labels for all the projections.
        
        Returns
        -------
        tuple of tuple of str
            tuple with the labels
        """
        axis_labels = []
        for idx0, idx1 in self.index_pairs:
            ax0, ax1 = self.axes_description[idx0], self.axes_description[idx1]
            ax0 = ax0[::-1]  # Flip for images
            axis_labels.append(
                tuple([self.format_axis_label(ax) for ax in [ax0, ax1]])
            )

        return tuple(axis_labels)

    def format_axis_label(self, axis):
        """Format the axes using full names.

        Parameters
        ----------
        axis : str from self.axes_description
            Axis to be formatted.

        Returns
        -------
        str
            Formatted string.

        """
        return "{} - {}".format(
            *[self.lims_labels[s].capitalize() for s in axis]
        )

    def __repr__(self):
        label_l = "<BGSpace SpaceConvention object>\n"
        origin_l = "origin: {}\n".format(
            tuple([self.lims_labels[s].capitalize() for s in self.origin])
        )
        sections_l = "sections: {}\n".format(
            tuple([f"{s.capitalize()} plane" for s in self.sections])
        )
        shape_l = "shape: {}\n".format(self.shape)

        return label_l + origin_l + sections_l + shape_l

    def __iter__(self):
        """Iter over origin, so that we can pass a SpaceConvention to
        instantiate a SpaceConvention.
        """
        for s in self.origin:
            yield s
