# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import os
import datetime

from swh.loader.tar import utils

# Static setup
EPOCH = 0
UTC_OFFSET = '+0000'
SWH_PERSON = 'Software Heritage'
SWH_MAIL = 'robot@softwareheritage.org'
REVISION_MESSAGE = 'synthetic revision message'
RELEASE_MESSAGE = 'synthetic release message'
REVISION_TYPE = 'tar'
REVISION = {
    'author_date': EPOCH,
    'author_offset': UTC_OFFSET,
    'author_name': SWH_PERSON,
    'author_email': SWH_MAIL,
    'committer_date': EPOCH,
    'committer_offset': UTC_OFFSET,
    'committer_name': SWH_PERSON,
    'committer_email': SWH_MAIL,
    'type': REVISION_TYPE,
    'message': REVISION_MESSAGE,
}
SWH_AUTHORITY = 1
GNU_AUTHORITY = 2


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


def _build_occurrence(tarpath, authority_id, validity_ts):
    """Build an occurrence from branch_name, authority_id and validity_ts.

    Args:
        - tarpath: file's path
        - authority_id: swh authority id (as per swh's storage values in
        organization table)
        - validity_ts: validity timestamp

    Returns:
        Occurrence dictionary
        - tarpath: file's path
        - authority: swh authority
        - validity: validity date (e.g. 2015-01-01 00:00:00+00)
    """
    validity = '%s+00' % datetime.datetime.utcfromtimestamp(validity_ts)
    return {
        'branch': os.path.basename(tarpath),
        'authority': authority_id,
        'validity': validity
    }


def swh_occurrence(tarpath):
    """Compute the occurrence from the tarpath with swh authority.

    Args:
        tarpath: file's path

    Returns:
        Occurrence dictionary (cf. _build_occurrence)

    """
    validity_ts = os.lstat(tarpath).st_ctime
    return _build_occurrence(tarpath, SWH_AUTHORITY, validity_ts)


def _time_from_path(tarpath):
    """Compute the modification time from the tarpath.

    """
    return os.lstat(tarpath).st_mtime


def gnu_occurrence(tarpath):
    """Compute the occurrence from the tarpath with gnu authority.

    Args:
        tarpath: file's path

    Return:
        Occurrence dictionary (cf. _build_occurrence)

    """
    validity_ts = _time_from_path(tarpath)
    return _build_occurrence(tarpath, GNU_AUTHORITY, validity_ts)


def compute_revision():
    return REVISION


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
            - offset: +0000
            - author_name: ''
            - author_email: ''
            - comment: ''

    """
    release_number = utils.release_number(filename)
    if release_number:
        return {
            'name': release_number,
            'date': _time_from_path(tarpath),
            'offset': UTC_OFFSET,
            'author_name': SWH_PERSON,
            'author_email': SWH_MAIL,
            'comment': RELEASE_MESSAGE,
        }
    return None
