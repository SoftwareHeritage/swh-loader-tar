# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import shutil
import tempfile

from swh.loader.dir import tasks
from swh.loader.tar import tarball


class LoadTarRepository(tasks.LoadDirRepository):
    """Import a tarball to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    CONFIG_BASE_FILENAME = 'loader/tar.ini'
    ADDITIONAL_CONFIG = {
        'extraction_dir': ('str', '/tmp/swh.loader.tar/'),
    }

    def run(self, tarpath, origin, revision, release, occurrences):
        """Import a tarball into swh.

        Args:
            - tarpath: path to a tarball file
            - origin, revision, release, occurrences: see LoadDirRepository.run

        """
        extraction_dir = self.config['extraction_dir']

        os.makedirs(extraction_dir, 0o755, exist_ok=True)

        dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                    dir=extraction_dir)

        if 'type' not in origin:  # let the type flow if present
            origin['type'] = 'tar'

        try:
            self.log.info('Uncompress %s to %s' % (tarpath, dir_path))
            tarball.uncompress(tarpath, dir_path)

            super().run(dir_path,
                        origin,
                        revision,
                        release,
                        occurrences)
        finally:  # always clean up
            shutil.rmtree(dir_path)
