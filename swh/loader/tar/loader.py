# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


import os
import tempfile
import requests
import shutil

from tempfile import mkdtemp

from swh.core import tarball
from swh.loader.core.loader import BufferedLoader
from swh.loader.dir.loader import revision_from, snapshot_from
from swh.model.hashutil import MultiHash
from swh.model.from_disk import Directory

from .build import compute_revision

try:
    from _version import __version__
except ImportError:
    __version__ = 'devel'


TEMPORARY_DIR_PREFIX_PATTERN = 'swh.loader.tar.'
DEBUG_MODE = '** DEBUG MODE **'


class LocalResponse:
    """Local Response class with iter_content api

    """
    def __init__(self, path):
        self.path = path

    def iter_content(self, chunk_size=None):
        with open(self.path, 'rb') as f:
            for chunk in f:
                yield chunk


class ArchiveFetcher:
    """Http/Local client in charge of downloading archives from a
       remote/local server.

    Args:
        temp_directory (str): Path to the temporary disk location used
                              for downloading the release artifacts

    """
    def __init__(self, temp_directory=None):
        self.temp_directory = temp_directory
        self.session = requests.session()
        self.params = {
            'headers': {
                'User-Agent': 'Software Heritage Tar Loader (%s)' % (
                    __version__
                )
            }
        }

    def download(self, url):
        """Download the remote tarball url locally.

        Args:
            url (str): Url (file or http*)

        Raises:
            ValueError in case of failing to query

        Returns:
            Tuple of local (filepath, hashes of filepath)

        """
        if url.startswith('file://'):
            # FIXME: How to improve this
            path = url.strip('file:').replace('///', '/')
            response = LocalResponse(path)
            length = os.path.getsize(path)
        else:
            response = self.session.get(url, **self.params, stream=True)
            if response.status_code != 200:
                raise ValueError("Fail to query '%s'. Reason: %s" % (
                    url, response.status_code))
            length = int(response.headers['content-length'])

        filepath = os.path.join(self.temp_directory, os.path.basename(url))

        h = MultiHash(length=length)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=None):
                h.update(chunk)
                f.write(chunk)

        actual_length = os.path.getsize(filepath)
        if length != actual_length:
            raise ValueError('Error when checking size: %s != %s' % (
                length, actual_length))

        hashes = {
            'length': length,
            **h.hexdigest()
        }
        return filepath, hashes


class TarLoader(BufferedLoader):
    """Tarball loader implementation.

    This is a subclass of the :class:DirLoader as the main goal of
    this class is to first uncompress a tarball, then provide the
    uncompressed directory/tree to be loaded by the DirLoader.

    This will:

    - creates an origin (if it does not exist)
    - creates a fetch_history entry
    - creates an origin_visit
    - uncompress locally the tarball in a temporary location
    - process the content of the tarballs to persist on swh storage
    - clean up the temporary location
    - write an entry in fetch_history to mark the loading tarball end (success
      or failure)
    """
    CONFIG_BASE_FILENAME = 'loader/tar'

    ADDITIONAL_CONFIG = {
        'working_dir': ('string', '/tmp'),
        'debug': ('bool', False),  # NOT FOR PRODUCTION
    }

    def __init__(self, logging_class='swh.loader.tar.TarLoader', config=None):
        super().__init__(logging_class=logging_class, config=config)
        self.local_cache = None
        self.dir_path = None
        working_dir = self.config['working_dir']
        os.makedirs(working_dir, exist_ok=True)
        self.temp_directory = mkdtemp(
            suffix='-%s' % os.getpid(),
            prefix=TEMPORARY_DIR_PREFIX_PATTERN,
            dir=working_dir)
        self.client = ArchiveFetcher(temp_directory=self.temp_directory)
        os.makedirs(working_dir, 0o755, exist_ok=True)
        self.dir_path = tempfile.mkdtemp(prefix='swh.loader.tar-',
                                         dir=self.temp_directory)
        self.debug = self.config['debug']

    def cleanup(self):
        """Clean up temporary disk folders used.

        """
        if self.debug:
            self.log.warn('%s Will not clean up temp dir %s' % (
                DEBUG_MODE, self.temp_directory
            ))
            return
        if os.path.exists(self.temp_directory):
            self.log.debug('Clean up %s' % self.temp_directory)
            shutil.rmtree(self.temp_directory)

    def prepare_origin_visit(self, *, origin, visit_date=None, **kwargs):
        self.origin = origin
        if 'type' not in self.origin:  # let the type flow if present
            self.origin['type'] = 'tar'
        self.visit_date = visit_date

    def prepare(self, *args, **kwargs):
        """last_modified is the time of last modification of the tarball.

        E.g https://ftp.gnu.org/gnu/8sync/:
            [ ] 8sync-0.1.0.tar.gz	2016-04-22 16:35 	217K
            [ ] 8sync-0.1.0.tar.gz.sig	2016-04-22 16:35 	543

        """
        self.last_modified = kwargs.get('last_modified')

    def fetch_data(self):
        """Retrieve and uncompress the archive.

        """
        # fetch the remote tarball locally
        url = self.origin['url']
        filepath, hashes = self.client.download(url)

        # add checksums in revision
        self.log.info('Uncompress %s to %s' % (filepath, self.dir_path))
        nature = tarball.uncompress(filepath, self.dir_path)

        dir_path = self.dir_path.encode('utf-8')
        directory = Directory.from_disk(path=dir_path, save_path=True)
        objects = directory.collect()
        if 'content' not in objects:
            objects['content'] = {}
        if 'directory' not in objects:
            objects['directory'] = {}

        # compute the full revision (with ids)
        revision = {
            **compute_revision(filepath, self.last_modified),
            'metadata': {
                'original_artifact': [{
                    'name': os.path.basename(filepath),
                    'archive_type': nature,
                    **hashes,
                }],
            }
        }
        revision = revision_from(directory.hash, revision)
        objects['revision'] = {
            revision['id']: revision,
        }

        branch_name = os.path.basename(self.dir_path)
        snapshot = snapshot_from(revision['id'], branch_name)
        objects['snapshot'] = {
            snapshot['id']: snapshot
        }
        self.objects = objects

    def store_data(self):
        objects = self.objects
        self.maybe_load_contents(objects['content'].values())
        self.maybe_load_directories(objects['directory'].values())
        self.maybe_load_revisions(objects['revision'].values())
        snapshot = list(objects['snapshot'].values())[0]
        self.maybe_load_snapshot(snapshot)
