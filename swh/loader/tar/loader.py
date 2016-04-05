# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import logging
import os
import tempfile
import shutil
import sys
import traceback

from swh.core import hashutil
from swh.loader.dir import loader
from swh.loader.tar import tarball, utils


class TarLoader(loader.DirLoader):
    """A tarball loader.

    """
    def __init__(self, config, origin_id):
        super().__init__(config, origin_id)
        self.log = logging.getLogger('swh.loader.tar.TarLoader')

    def process(self, tarpath, origin, revision, release, occurrences):
        """Load a tarball in backend.

        This will:
        - persist the origin if it does not exist.
        - write an entry in fetch_history to mark the loading tarball start
        - uncompress locally the tarballs in a temporary location
        - process the content of the tarballs to persist on swh storage
        - clean up the temporary location
        - write an entry in fetch_history to mark the loading tarball end

        Args:
            - tarpath: path to the tarball to uncompress
            - origin: Dictionary origin
              - url: url origin we fetched
              - type: type of the origin
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
            - release: Dictionary of information needed, keys are:
              - name: release name
              - date: release timestamp (e.g. 1444054085)
              - offset: release date offset e.g. -0220, +0100
              - author_name: release author's name
              - author_email: release author's email
              - comment: release's comment message
            - occurrences: List of occurrence dictionary.
              Information needed, keys are:
              - branch: occurrence's branch name
              - authority_id: authority id (e.g. 1 for swh)
              - validity: validity date (e.g. 2015-01-01 00:00:00+00)

        """
        if 'type' not in origin:  # let the type flow if present
            origin['type'] = 'tar'

        origin['id'] = self.storage.origin_add_one(origin)

        # Mark the start of the loading
        fetch_history_id = self.open_fetch_history(origin['id'])

        # Prepare the extraction path
        extraction_dir = self.config['extraction_dir']
        os.makedirs(extraction_dir, 0o755, exist_ok=True)
        dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                    dir=extraction_dir)

        # add checksums in revision
        artifact = utils.convert_to_hex(hashutil.hashfile(tarpath))
        artifact['name'] = os.path.basename(tarpath)

        # for edge cases (NotImplemented...)
        result = {'status': False, 'stderr': ''}

        try:
            self.log.info('Uncompress %s to %s' % (tarpath, dir_path))
            nature = tarball.uncompress(tarpath, dir_path)
            artifact['archive_type'] = nature
            artifact['length'] = os.path.getsize(tarpath)

            revision['metadata'] = {
                'original_artifact': [artifact],
            }

            result = super().process(dir_path, origin, revision, release,
                                     occurrences)
        except:
            e_info = sys.exc_info()
            if not result['status']:
                # Enrich the error message with the tarball
                result['stderr'] = 'reason:%s\ntrace:%s\n%s' % (
                    e_info[1],
                    ''.join(traceback.format_tb(e_info[2])),
                    result.get('stderr', ''))

            raise
        finally:
            shutil.rmtree(dir_path)

            if not result['status']:
                result['stderr'] = 'archive:%s\nreason:%s' % (
                    tarpath,
                    result.get('stderr', ''))

            # mark the end of the loading
            self.close_fetch_history(fetch_history_id, result)
