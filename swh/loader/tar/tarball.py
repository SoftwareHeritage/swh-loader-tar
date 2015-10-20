# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import tarfile
import zipfile


_module_fn = {
    'tar': tarfile,
    'zip': zipfile
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
        m = _module_fn[self.nature]
        with m.open(self.path) as archive:
            archive.extractall(path=dir_path)

    def to_dict(self):
        return {
            'nature': self.nature,
            'path': self.path,
            'name': self.name
        }
