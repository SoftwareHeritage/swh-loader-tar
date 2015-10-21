# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import tarfile
import zipfile


def uncompress_zip(tarpath, dirpath):
    """Uncompress zip adapter function.

    """
    with zipfile.ZipFile(tarpath) as z:
        z.extractall(path=dirpath)


def uncompress_tar(tarpath, dirpath):
    """Uncompress tar adapter function.

    """
    with tarfile.open(tarpath) as t:
        t.extractall(path=dirpath)


_uncompress_fn = {
    'tar': uncompress_tar,
    'zip': uncompress_zip
}


def nature(tarpath):
    """Determine if tarpath represents a tarball.

    Args:
        tarpath: absolute filepath to archive file

    Returns:
        'tar', 'zip' or None depending on tarpath's nature.

    """
    if tarfile.is_tarfile(tarpath):
        return 'tar'
    if zipfile.is_zipfile(tarpath):
        return 'zip'
    return None


class Tarball():
    """SWH tarball representation.

    - nature: tar, zip supported
    - name: tar file's name
    - path: absolute path to tarball

    """
    def __init__(self, nature, name, path):
        self.nature = nature
        self.name = name
        self.path = path

    def extract(self, dir_path):
        """Extract the current archive to dir_path.

           At the end of this call, dir_path contains the tarball's
           uncompressed content.

           Args:
               tar_path: the path to access the tarball
               dir_path: The path where to extract the tarball's content.
        """
        _uncompress_fn[self.nature](self.path, dir_path)

    def to_dict(self):
        return {
            'nature': self.nature,
            'path': self.path,
            'name': self.name
        }
