import numpy as np
from scipy import ndimage as nd

from bg_space.utils import ordered_list_from_set
import warnings
from functools import wraps


def to_target(method):
    """Decorator for bypassing SpaceConvention creation.
    """

    @wraps(method)
    def decorated(spaceconv_instance, space_description, *args, **kwargs):

        # isinstance(..., SpaceConvention) here would fail, so:
        if not type(space_description) == type(spaceconv_instance):
            # Generate description if input was not one:
            sc_args = {
                k: kwargs.pop(k)
                for k in ["shape", "resolution", "offset"]
                if k in kwargs.keys()
            }
            space_description = SpaceConvention(space_description, **sc_args)

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

    >>> SpaceConvention("asl")
    >>> SpaceConvention(["a", "s", "l"])
    >>> SpaceConvention(["anterior", "superior", "left"])

    This can be convenient for quickly reorient a stack to match different
    axes convention.

    More advanced usage include resampling in new space resolution, and addition
    of offsets, useful for stack cropping/padding.
    Note however that combination of these features with very differently
    oriented stacks (eg, with different axes directions) can be confusing!

    Parameters
    ----------
    origin : str or tuple of str or list of str
        Each letter or initial of each string should match a letter in
        space_specs.
    shape : 3 elements tuple, optional
        Shape of the bounding box of the space (e.g. shape of a stack)
        (default=None).
    resolution : 3 elements tuple, optional
        Resolution of the stack for resampling (in any unit, as long as they
        are consistent across stacks) (default=None).
    offset : 3 elements tuple, optional
        Offset of the space, if present - relative to another atlas, in any
        unit consistent with the resolution (default=(0, 0, 0)).
    """

    # Use sets to avoid any explicit convention definition:
    space_axes = {
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

    def __init__(self, origin, shape=None, resolution=None, offset=(0, 0, 0)):

        self.shape = shape
        self.resolution = resolution
        self.offset = offset

        # Reformat to lowercase initial:
        origin = [o[0].lower() for o in origin]

        axs_description = []

        # Loop over origin specification:
        for lim in origin:

            # Loop over possible axes and origin values:
            for k, possible_lims in self.space_axes.items():

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
                k for k, val in self.space_axes.items() if lims[0] in val
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
        """Find axes reordering, flips, ratios and offsets required to go to
        target space convention.
        The order of flips, ratios and offsets is the one of the target space!

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
        tuple
            Scale factors to move target space (in target axis order).
        tuple
            Offsets to move target space (in target axis order and resolution).

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

        # Calculate scales if resolutions are specified:
        if self.resolution is not None and target.resolution is not None:
            scales = tuple(
                [
                    self.resolution[si] / target.resolution[ti]
                    for ti, si in enumerate(order)
                ]
            )
        else:
            scales = (1, 1, 1)

        if self.offset is not None and target.offset is not None:
            offsets = tuple(
                [
                    (self.offset[si] - target.offset[ti]) * scales[ti]
                    for ti, si in enumerate(order)
                ]
            )
        else:
            offsets = (0, 0, 0)

        return order, flips, scales, offsets

    @to_target
    def map_stack_to(
        self, target, stack, copy=False, to_target_shape=False, interp_order=3
    ):
        """Transpose and flip stack to move it to target space convention.

        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.
        stack : numpy array
            Stack to map from space convention a to space convention b
        copy : bool, optional
            If true, stack is copied (default=False).
        to_target_shape : bool, optional
            If true, stack is padded or cropped to fit target shape. Default
            is false, but if a non-0 offset is calculated it is set to True.
        interp_order : int, optional
            Order of the spline for interpolation in zoom function, used only
            in resampling. Default is 3 (scipy default), use 0 for nearest
            neighbour resampling.
        Returns
        -------

        """

        # Find order swapping and flips:
        order, flips, scales, offsets = self.map_to(target)

        # If we want to work on a copy, create:
        if copy:
            stack = stack.copy()

        # Transpose axes:
        stack = np.transpose(stack, order)

        # Flip as required:
        stack = np.flip(stack, [i for i, f in enumerate(flips) if f])

        # If zooming is required, resample using scipy:
        if scales != (1, 1, 1):
            stack = nd.zoom(stack, scales, order=interp_order)

        # if offset is required, crop and pad:
        if offsets != (0, 0, 0) and to_target_shape:
            empty_stack = np.zeros(target.shape)

            slices_target = []
            slices_stack = []
            for s_sh, t_sh, o in zip(stack.shape, target.shape, offsets):
                o = int(o)  # convert to use in indices

                # Warn if stack to be mapped is out of target shape:
                if o >= t_sh or (o < 0 and -o >= s_sh):
                    warnings.warn(
                        "Stack is out of target shape on at least one axis, mapped stack will be empty!"
                    )
                    return empty_stack
                else:
                    # Prepare slice lists for source and target:
                    slices_target.append(slice(max(0, o), o + s_sh))
                    slices_stack.append(slice(-min(0, o), t_sh - o))

            empty_stack[tuple(slices_target)] = stack[tuple(slices_stack)]

            return empty_stack

        return stack

    @to_target
    def transformation_matrix_to(self, target):
        """Find transformation matrix going to target space convention.

        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.

        Returns
        -------

        """
        # shape = shape if shape is not None else self.shape
        shape = self.shape

        # Find axes order and flips:
        order, flips, scales, offsets = self.map_to(target)

        # Instantiate transformation matrix:
        transformation_mat = np.zeros((4, 4))
        transformation_mat[-1, -1] = 1

        # Fill it in the required places:
        for ai, bi in enumerate(order):
            # Add the ones for the flips and swaps:
            transformation_mat[ai, bi] = (
                -scales[ai] if flips[ai] else scales[ai]
            )

            # If flipping is necessary, we also need to translate origin:
            if shape is None and flips[ai]:
                raise TypeError(
                    "The source space should have a shape for this transformation!"
                )
            origin_offset = shape[bi] if flips[ai] else 0
            origin_offset += offsets[ai]  # add space offset

            transformation_mat[ai, 3] = origin_offset

        return transformation_mat

    @to_target
    def map_points_to(self, target, pts):
        """Map points to target space convention.
        Parameters
        ----------
        target : SpaceConvention object
            Target space convention.
        pts : (n, 3) list/tuple (of lists/tuples) or numpy array
            Array with the points to be mapped.

        Returns
        -------
        (n, 3) numpy array
            Array with the transformed points.
        """

        # Ensure correct formatting of pts:
        pts = np.array(pts)
        if len(pts.shape) == 1:
            pts = pts[np.newaxis, :]
        transformation_mat = self.transformation_matrix_to(target)

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
    def plane_normals(self):
        """Dictionary of normals for the planes in the space.
        """
        return {
            k: (0, 0, 0)[:i] + (1,) + (0, 0)[i:]
            for i, k in enumerate(self.sections)
        }

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
