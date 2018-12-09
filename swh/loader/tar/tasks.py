# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.scheduler.task import Task

from swh.loader.tar.loader import RemoteTarLoader


class LoadTarRepository(Task):
    """Import a remote or local archive to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    def run_task(self, *, origin, visit_date, last_modified):
        """Import a tarball into swh.

        Args: see :func:`TarLoader.prepare`.

        """
        loader = RemoteTarLoader()
        loader.log = self.log
        return loader.load(
            origin=origin, visit_date=visit_date, last_modified=last_modified)
