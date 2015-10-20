#!/usr/bin/env python3

import os
import tarfile
import zipfile


def is_tarball(filepath):
    """Determine if the filepath is an tarball or not.

    This is dependent on the filepath only.

    Args:
        filepath: the filepath without any paths.

    Returns:
        Boolean True if an tarball, False otherwise.

    """

    return tarfile.is_tarfile(filepath) or zipfile.is_zipfile(filepath)


def list_tarballs_from(path):
    """From path, produce tarball tarball message to celery.

    Args:
        path: top directory to list tarballs from.

    """
    for dirpath, dirnames, filenames in os.walk(path):
        for fname in filenames:
            tarpath = os.path.join(dirpath, fname)
            if os.path.exists(tarpath) and is_tarball(tarpath):
                yield dirpath, fname


def count_tarballs_from(path):
    count = 0
    for dirpath, fname in list_tarballs_from(path):
        count += 1

    return count


if __name__ == '__main__':
    for path in ['/home/storage/space/mirrors/gnu.org/gnu',
                 '/home/storage/space/mirrors/gnu.org/old-gnu']:
        print("%s %s" % (path, count_tarballs_from(path)))
