# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import tarfile
import zipfile
import shutil


def is_tarball(filepath):
    """Given a filepath, determine if it represents an archive.

    """
    return tarfile.is_tarfile(filepath) or zipfile.is_zipfile(filepath)

uncompress = shutil.unpack_archive
