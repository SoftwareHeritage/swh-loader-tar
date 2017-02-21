# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.scheduler.task import Task

from swh.loader.tar.loader import TarLoader


class LoadTarRepository(Task):
    """Import a directory to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    def run(self, tarpath, origin, revision, occurrences):
        """Import a tarball into swh.

        Args:
            - tarpath: path to a tarball file
            - origin, revision, release, occurrences:
              cf. swh.loader.dir.loader.run docstring

        """
        loader = TarLoader()
        loader.log = self.log
        loader.prepare_and_load(tarpath, origin, revision, occurrences)
