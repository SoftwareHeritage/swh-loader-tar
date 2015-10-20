# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import shutil
import tempfile
import tarfile

from swh.loader.dir import tasks


def uncompress(tar_path, dir_path):
    """Decompress an archive tar_path to dir_path.

    At the end of this call, dir_path contains the tarball's
    uncompressed content.

    Args:
        tar_path: the path to access the tarball
        dir_path: The path where to extract the tarball's content.
    """
    with tarfile.open(tar_path) as tarball:
        tarball.extractall(path=dir_path)


class LoadTarRepository(tasks.LoadDirRepository):
    """Import a tarball to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    CONFIG_BASE_FILENAME = 'loader/tar.ini'
    ADDITIONAL_CONFIG = {
        'extraction_dir': ('str', '/tmp/swh.loader.tar/'),
    }

    def run(self, tar_path, origin, revision, release, occurrences):
        """Import a tarball tar_path.

        Args:
            - tar_path: path access to the tarball
            - origin, revision, release, occurrences: see LoadDirRepository.run

        """
        extraction_dir = self.config['extraction_dir']
        dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                    dir=extraction_dir)

        self.log.info('Uncompress %s to %s' % (tar_path, dir_path))
        uncompress(tar_path, dir_path)

        if 'type' not in origin:  # let the type flow if present
            origin['type'] = 'tar'

        try:
            super().run(dir_path, origin, revision, release, occurrences)
        finally:  # always clean up
            shutil.rmtree(dir_path)


class LoadTarRepositoryPrint(tasks.LoadDirRepository):
    """Import a tarball to Software Heritage

    DEBUG purposes
    """
    task_queue = 'swh_loader_tar_print'

    def run(self, tar_path, origin, revision, release, occurrences):
        """Import a tarball tar_path.

        Args:
            - tar_path: path access to the tarball
            - origin, revision, release, occurrences: see LoadDirRepository.run

        """
        print(tar_path, origin, revision, release, occurrences)
