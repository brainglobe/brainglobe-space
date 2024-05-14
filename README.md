[![Python Version](https://img.shields.io/pypi/pyversions/brainglobe-space.svg)](https://pypi.org/project/brainglobe-space)
[![PyPI](https://img.shields.io/pypi/v/brainglobe-space.svg)](https://pypi.org/project/brainglobe-space)
[![Downloads](https://pepy.tech/badge/brainglobe-space)](https://pepy.tech/project/brainglobe-space)
[![Wheel](https://img.shields.io/pypi/wheel/brainglobe-space.svg)](https://pypi.org/project/brainglobe-space)
[![Development Status](https://img.shields.io/pypi/status/brainglobe-space.svg)](https://github.com/brainglobe/brainglobe-space)
[![Tests](https://img.shields.io/github/actions/workflow/status/brainglobe/brainglobe-space/test_and_deploy.yml?branch=main)](https://github.com/brainglobe/brainglobe-space/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainglobe-space/branch/main/graph/badge.svg?token=nx1lhNI7ox)](https://codecov.io/gh/brainglobe/brainglobe-space)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](https://brainglobe.info/community/developers/index.html)
[![Twitter](https://img.shields.io/twitter/follow/brain_globe?style=social)](https://twitter.com/brain_globe)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/267813717.svg)](https://zenodo.org/doi/10.5281/zenodo.4552536)


# brainglobe-space

Anatomical space conventions made easy.

Working with anatomical images, one often encounters the problem of matching the orientation of stacks with different conventions about axes orientation and order. Moreover, when multiple swaps and flips are involved, it can be annoying to map the same transformations to volumes and points (e.g., coordinates or meshes).

`brainglobe-space` provides a neat way of defining an anatomical space, and of operating stacks and point transformations between spaces.

If you use `brainglobe-space` for your analyses, please cite its [Zenodo DOI](https://zenodo.org/record/4552537#.YDAFzi1Q2Rs!) <https://zenodo.org/record/4552537#.YDAFzi1Q2Rs!>

## Installation

You can install `brainglobe-space` with:

```bash
pip install brainglobe-space
```

## Usage

To define a new anatomical space, it is sufficient to give the directions of the stack origin position:

```python
source_origin = ("Left", "Superior", "Anterior")
target_origin = ("Inferior", "Posterior", "Right")
```

A stack can be then easily transformed from the source to the target space:

```python
import brainglobe_space as bg
import numpy as np
stack = np.random.rand(3, 2, 4)

mapped_stack = bg.map_stack_to(source_origin, target_origin, stack)
```

The transformation is handled only with numpy index operations; *i.e.*, no complex
image affine transformations are applied. This is often useful as the preparatory step for starting any kind of image registration.

A shortened syntax can be used to define a space using initials of the origin directions:

```python
mapped_stack = bg.map_stack_to("lsa", "ipr", stack)
```

---

## NOTE

When you work with a stack, the origin is the upper left corner when you show the first element `stack[0, :, :]` with matplotlib or when you open the stack with ImageJ. First dimension is the one that you are slicing, the second the height of the image, and the third the width of the image.

---

## The `AnatomicalSpace` class

Sometimes, together with the stack we have to move a set of points (cell coordinates, meshes, etc.). This introduces the additional complexity of keeping track, together with the axes swaps and flips, of the change of the origin offset.

To handle this situation, we can define a source space using the `AnatomicalSpace`
class, specifying also the stack shape:

```python

stack = np.random.rand(3, 2, 4)  # a stack in source space
annotations = np.array([[0, 0, 0], [2, 1, 3]])  # related point annotations

source_space = bg.AnatomicalSpace(target_origin, stack.shape)

mapped_stack = source_space.map_stack_to("ipr", stack)  # transform the stack
mapped_annotations = source_space.map_points_to("ipr", annotations)  # transform the points
```

The points are transformed through the generation of a transformation matrix.
Finally, if we want to log this matrix (e.g., to reconstruct the full transformations sequence of a registration), we can get it:

```python
target_space = bg.AnatomicalSpace("ipr", stack.shape)
transformation_matrix = source_space.transformation_matrix_to(target_space)
# equivalent to:
transformation_matrix = source_space.transformation_matrix_to("ipr", stack.shape)
```

The target get always be defined as a `bg.AnatomicalSpace` object, or a valid origin specification plus a shape (the shape is required only if axes flips are required).

## Matching space resolutions and offsets

The `AnatomicalSpace` class can deal also with stack resampling/padding/cropping. This requires simply specifying values for resolutions and offsets when instantiating a `AnatomicalSpace` object. Once that is done, using `AnatomicalSpace.transformation_matrix_to` creating affine transformation matrices from one space to the other will be a piece of cake!

```python
source_space = bgs.AnatomicalSpace("asl", resolution=(2, 1, 2), offset=(1, 0, 0))
target_space = bgs.AnatomicalSpace("sal", resolution=(1, 1, 1), offset=(0, 0, 2))
source_space.transformation_matrix_to(target_space)
```

Moreover, we can now use those space objects to resample stacks, and to generate stacks matching a target shape with the correct padding/cropping simply by specifying a target offset:

```python
source_space = bgs.AnatomicalSpace("asl", resolution=(2, 1, 2), offset=(1, 0, 0))
target_space = bgs.AnatomicalSpace("asl", resolution=(1, 1, 1), shape=(5, 4, 2))  # we need a target shape
source_space.transformation_matrix_to(target_space, stack, to_target_shape=True)
```

## Easy iteration over projections

Finally, another convenient feature of BGSpace is the possibility of iterating easily through the projections of the stack and generate section names and axes labels:

```python
sc = bg.AnatomicalSpace("asl")  # origin for the stack to be plotted

for i, (plane, labels) in enumerate(zip(sc.sections, sc.axis_labels)):
    axs[i].imshow(stack.mean(i))

    axs[i].set_title(f"{plane.capitalize()} view")
    axs[i].set_ylabel(labels[0])
    axs[i].set_xlabel(labels[1])
```

![Projection illustrations](/docs/img/projections.png)

## Contributing

Contributions are very welcome. Please see the [developers guide](https://brainglobe.info/developers/index.html).
