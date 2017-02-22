# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import itertools
import random

from swh.core import hashutil


def commonname(path0, path1, as_str=False):
    """Compute the commonname between the path0 and path1.

    """
    return path1.split(path0)[1]


def convert_to_hex(d):
    """Convert a flat dictionary with bytes in values to the same dictionary
    with hex as values.

    Args:
        dict: flat dictionary with sha bytes in their values.

    Returns:
        Mirror dictionary with values as string hex.

    """
    if not d:
        return d

    checksums = {}
    for key, h in d.items():
        checksums[key] = hashutil.hash_to_hex(h)

    return checksums


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
        l = list(iterable)
        random.shuffle(l)
        for e in l:
            yield e
