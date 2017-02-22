# Copyright (C) 2015-2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import os
import tempfile
import shutil

from swh.core import hashutil
from swh.loader.dir import loader
from swh.loader.tar import tarball, utils


class TarLoader(loader.DirLoader):
    """A tarball loader:

        - creates an origin if it does not exist
        - creates a fetch_history entry
        - creates an origin_visit
        - uncompress locally the tarballs in a temporary location
        - process the content of the tarballs to persist on swh storage
        - clean up the temporary location
        - write an entry in fetch_history to mark the loading tarball end
        (success or failure)

        Args:
            - tarpath: path to the tarball to uncompress
            - origin: Dictionary origin
              - url: url origin we fetched
              - type: type of the origin
            - visit_date (str): To override the visit date
            - revision: Dictionary of information needed, keys are:
              - author_name: revision's author name
              - author_email: revision's author email
              - author_date: timestamp (e.g. 1444054085)
              - author_offset: date offset e.g. -0220, +0100
              - committer_name: revision's committer name
              - committer_email: revision's committer email
              - committer_date: timestamp
              - committer_offset: date offset e.g. -0220, +0100
              - type: type of revision dir, tar
              - message: synthetic message for the revision
            - occurrences: List of occurrence dictionary.
              Information needed, keys are:
              - branch: occurrence's branch name
              - authority_id: authority id (e.g. 1 for swh)
              - validity: validity date (e.g. 2015-01-01 00:00:00+00)

    """
    CONFIG_BASE_FILENAME = 'loader/tar'

    ADDITIONAL_CONFIG = {
        'extraction_dir': ('string', '/tmp')
    }

    def __init__(self):
        super().__init__(logging_class='swh.loader.tar.TarLoader')

    def prepare(self, *args, **kwargs):
        """1. Uncompress the tarball in a temporary directory.
           2. Compute some metadata to update the revision.

        """
        tarpath, origin, visit_date, revision, occs = args

        if 'type' not in origin:  # let the type flow if present
            origin['type'] = 'tar'

        # Prepare the extraction path
        extraction_dir = self.config['extraction_dir']
        os.makedirs(extraction_dir, 0o755, exist_ok=True)
        dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                    dir=extraction_dir)

        # add checksums in revision
        artifact = utils.convert_to_hex(hashutil.hashfile(tarpath))
        artifact['name'] = os.path.basename(tarpath)

        self.log.info('Uncompress %s to %s' % (tarpath, dir_path))
        nature = tarball.uncompress(tarpath, dir_path)
        artifact['archive_type'] = nature
        artifact['length'] = os.path.getsize(tarpath)

        revision['metadata'] = {
            'original_artifact': [artifact],
        }

        self.dir_path = dir_path

        super().prepare(dir_path, origin, visit_date, revision, None, occs)

    def cleanup(self):
        """Clean up temporary directory where we uncompress the tarball.

        """
        dir_path = self.dir_path
        if dir_path and os.path.exists(dir_path):
            shutil.rmtree(dir_path)
