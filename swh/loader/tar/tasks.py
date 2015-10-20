# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import shutil
import tempfile

from swh.loader.dir import tasks


class LoadTarRepository(tasks.LoadDirRepository):
    """Import a tarball to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    CONFIG_BASE_FILENAME = 'loader/tar.ini'
    ADDITIONAL_CONFIG = {
        'extraction_dir': ('str', '/tmp/swh.loader.tar/'),
    }

    def run(self, tarball, origin, revision, release, occurrences):
        """Import a tarball tar_path.

        Args:
            - tarball: a tarball object
            - origin, revision, release, occurrences: see LoadDirRepository.run

        """
        extraction_dir = self.config['extraction_dir']
        dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                    dir=extraction_dir)

        self.log.info('Uncompress %s to %s' % (tarball.path, dir_path))
        tarball.extract(dir_path)

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
