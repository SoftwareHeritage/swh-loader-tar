# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import itertools
import random


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Args:
        iterable: an iterable
        n: size of block
        fillvalue: value to use for the last block

    Returns:
        fixed-length chunks of blocks as iterables

    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def random_blocks(iterable, block=100, fillvalue=None):
    """Given an iterable:
    - slice the iterable in data set of block-sized elements
    - randomized the data set
    - yield each element

    Args:
        iterable: iterable of data
        block: number of elements per block
        fillvalue: a fillvalue for the last block if not enough values in
        last block

    Returns:
        An iterable of randomized per block-size elements.

    """
    count = 0
    for iterable in grouper(iterable, block, fillvalue=fillvalue):
        count += 1
        lst = list(iterable)
        random.shuffle(lst)
        for e in lst:
            yield e
