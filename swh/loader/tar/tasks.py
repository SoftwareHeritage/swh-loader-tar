# Copyright (C) 2015-2016  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.loader.core import tasks

from swh.loader.tar.loader import TarLoader


class LoadTarRepository(tasks.LoaderCoreTask):
    """Import a directory to Software Heritage

    """
    task_queue = 'swh_loader_tar'

    def run(self, tarpath, origin, revision, release, occurrences):
        """Import a tarball into swh.

        Args:
            - tarpath: path to a tarball file
            - origin, revision, release, occurrences:
              cf. swh.loader.dir.loader.run docstring

        """
        storage = TarLoader().storage

        if 'type' not in origin:  # let the type flow if present
            origin['type'] = 'tar'

        origin['id'] = storage.origin_add_one(origin)

        fetch_history_id = self.open_fetch_history(storage, origin['id'])

        result = TarLoader(origin['id']).process(tarpath,
                                                 origin,
                                                 revision,
                                                 release,
                                                 occurrences)

        self.close_fetch_history(storage, fetch_history_id, result)
