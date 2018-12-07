# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import random

from swh.core.utils import grouper


def random_blocks(iterable, block=100, fillvalue=None):
    """Given an iterable:

    - slice the iterable in data set of block-sized elements
    - randomized the block-sized elements
    - yield each element of that randomized block-sized
    - continue onto the next block-sized block

    Args:
        iterable (Iterable): an iterable
        block (int): number of elements per block
        fillvalue (Optional[Something]): value to use as fill-in
          values (typically for the last loop, the iterable might be
          less than n elements). None by default but could be anything
          relevant for the caller (e.g tuple of (None, None))

    Yields:
        random elements per size of block

    """
    count = 0
    for iter_ in grouper(iterable, block, fillvalue=fillvalue):
        count += 1
        lst = list(iter_)
        random.shuffle(lst)
        for e in lst:
            yield e
