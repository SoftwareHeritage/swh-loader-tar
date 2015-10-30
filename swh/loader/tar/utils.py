# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import itertools
import random
import re

from swh.core import hashutil


# FIXME; extract this in property
# to recognize existing naming pattern
extensions = [
    'ps',
    'zip',
    'tar',
    'gz', 'tgz',
    'bz2', 'bzip2',
    'lzma', 'lz',
    'xz',
    'Z',
    'diff',
    'iso',
    'exe',
    'jar',
    'egg',
    'gem',
    'xpi',
    'apk',
    'dmg',
    'DevPak',
]


pattern = re.compile(r'''
^
(?:
    # We have a software name and a release number, separated with a
    # -, _ or dot.
    (?P<software_name1>.+?[-_.])
    (?P<release_number>[0-9][0-9a-zA-Z_.+:~-]*?)
|
    # We couldn't match a release number, put everything in the
    # software name.
    (?P<software_name2>.+?)
)
(?P<extension>(?:\.(?:%s))+)
$
''' % '|'.join(extensions),
     flags=re.VERBOSE)


def parse_filename(filename):
    """Parse a filename into its components.

    Parsing policy:
    We use Debian's release number heuristic: A release number starts
    with a digit, and is followed by alphanumeric characters or any of
    ., +, :, ~ and -

    We hardcode a list of possible extensions, as this release number
    scheme would match them too... We match on any combination of those.

    Greedy matching is done right to left (we only match the extension
    greedily with +, software_name and release_number are matched lazily
    with +? and *?).

    Args:
        filename: filename without path.

    Returns:
        Dictionary with the following keys:
        - software_name
        - release_number: can be None if it could not be found.
        - extension

    Raises:
        ValueError if the filename could not be parsed.

"""
    m = pattern.match(filename)
    if not m:
        raise ValueError('Filename %s could not be parsed.' % filename)

    d = m.groupdict()
    return {
        'software_name': d['software_name1'] or d['software_name2'],
        'release_number': d['release_number'],
        'extension': d['extension'],
    }


def release_number(filename):
    """Compute the release number from the filename.

    cf. parse_filename's docstring

    """
    return parse_filename(filename)['release_number']


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
