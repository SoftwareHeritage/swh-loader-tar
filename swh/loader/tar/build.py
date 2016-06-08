# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

from swh.loader.tar import utils


# Static setup
EPOCH = 0
UTC_OFFSET = 0
SWH_PERSON = {
    'name': 'Software Heritage',
    'fullname': 'Software Heritage',
    'email': 'robot@softwareheritage.org'
}
REVISION_MESSAGE = 'synthetic revision message'
RELEASE_MESSAGE = 'synthetic release message'
REVISION_TYPE = 'tar'


def compute_origin(url_scheme, url_type, root_dirpath, tarpath):
    """Compute the origin.

    Args:
        - url_scheme: scheme to build the origin's url
        - url_type: origin's type
        - root_dirpath: the top level root directory path
        - tarpath: file's absolute path

    Returns:
        Dictionary origin with keys:
       - url: origin's url
       - type: origin's type

    """
    relative_path = utils.commonname(root_dirpath, tarpath)
    return {
        'url': ''.join([url_scheme,
                        os.path.dirname(relative_path)]),
        'type': url_type,
    }


def occurrence_with_date(date, tarpath):
    """Compute the occurrence using the tarpath's ctime.

    Args:
        authority: the authority's uuid
        tarpath: file's path

    Returns:
        Occurrence dictionary (cf. _build_occurrence)

    """
    return {
        'branch': os.path.basename(tarpath),
        'date': date
    }


def _time_from_path(tarpath):
    """Compute the modification time from the tarpath.

    """
    return os.lstat(tarpath).st_mtime


def compute_revision(tarpath):
    """Compute a revision.

    Args:
        tarpath: absolute path to the tarball

    Returns:
        Revision as dict:
        - date: the modification timestamp as returned by a fstat call
        - committer_date: the modification timestamp as returned by a fstat
        call
        - author: cf. SWH_PERSON
        - committer: cf. SWH_PERSON
        - type: cf. REVISION_TYPE
        - message: cf. REVISION_MESSAGE

    """
    ts = _time_from_path(tarpath)
    return {
        'date': {
            'timestamp': ts,
            'offset': UTC_OFFSET,
        },
        'committer_date': {
            'timestamp': ts,
            'offset': UTC_OFFSET,
        },
        'author': SWH_PERSON,
        'committer': SWH_PERSON,
        'type': REVISION_TYPE,
        'message': REVISION_MESSAGE,
    }


def compute_release(filename, tarpath):
    """Compute a release from a given tarpath, filename.
    If the tarpath does not contain a recognizable release number, the release
    can be skipped.

    Args:
        filename: file's name without path
        tarpath: file's absolute path

    Returns:
        None if the release number cannot be extracted from the filename.
        Otherwise a synthetic release is computed with the following keys:
            - name: the release computed from the filename
            - date: the modification timestamp as returned by a fstat call
            - offset: 0
            - author_name: ''
            - author_email: ''
            - comment: ''

    """
    release_number = utils.release_number(filename)
    if release_number:
        return {
            'name': release_number,
            'date': {
                'timestamp': _time_from_path(tarpath),
                'offset': UTC_OFFSET,
            },
            'author': SWH_PERSON,
            'message': RELEASE_MESSAGE,
        }
    return None
