# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import re


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
    'gem'
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
