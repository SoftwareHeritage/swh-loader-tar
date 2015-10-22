# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import tarfile
import zipfile


def is_tarball(filepath):
    """Given a filepath, determine if it represents an archive.

    Args:
        filepath: file to test for tarball property

    Returns:
        Bool, True if it's a tarball, False otherwise

    """
    return tarfile.is_tarfile(filepath) or zipfile.is_zipfile(filepath)


def _uncompress_zip(tarpath, dirpath):
    """Uncompress zip adapter function.

    """
    with zipfile.ZipFile(tarpath) as z:
        z.extractall(path=dirpath)


def _uncompress_tar(tarpath, dirpath):
    """Uncompress tar adapter function.

    """
    with tarfile.open(tarpath) as t:
        t.extractall(path=dirpath)


def uncompress(tarpath, dest):
    """Uncompress tarpath to dest.

    FIXME: Beware badly formatted archive (with / and .., cf.
    https://docs.python.org/3.4/library/tarfile.html#tarfile.TarFile.extractall
    warning).

    """
    if tarfile.is_tarfile(tarpath):
        _uncompress_tar(tarpath, dest)
    elif zipfile.is_zipfile(tarpath):
        _uncompress_zip(tarpath, dest)
    else:
        raise ValueError('File %s is not a supported archive.' % tarpath)
