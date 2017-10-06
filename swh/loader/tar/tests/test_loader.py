# Copyright (C) 2017  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from unittest import TestCase

from nose.plugins.attrib import attr
from nose.tools import istest

from swh.loader.tar.loader import TarLoader


class LoaderNoStorageForTest:
    """Mixin class to inhibit the persistence and keep in memory the data
    sent for storage.

    cf. SWHTarLoaderNoStorage

    """
    def __init__(self):
        super().__init__()
        # Init the state
        self.all_contents = []
        self.all_directories = []
        self.all_revisions = []
        self.all_releases = []
        self.all_occurrences = []

    def send_origin(self, origin):
        self.origin = origin

    def send_origin_visit(self, origin_id, ts):
        self.origin_visit = {
            'origin': origin_id,
            'ts': ts,
            'visit': 1,
        }
        return self.origin_visit

    def update_origin_visit(self, origin_id, visit, status):
        self.status = status
        self.origin_visit = visit

    def maybe_load_contents(self, all_contents):
        self.all_contents.extend(all_contents)

    def maybe_load_directories(self, all_directories):
        self.all_directories.extend(all_directories)

    def maybe_load_revisions(self, all_revisions):
        self.all_revisions.extend(all_revisions)

    def maybe_load_releases(self, releases):
        self.all_releases.extend(releases)

    def maybe_load_occurrences(self, all_occurrences):
        self.all_occurrences.extend(all_occurrences)

    def open_fetch_history(self):
        return 1

    def close_fetch_history_success(self, fetch_history_id):
        pass

    def close_fetch_history_failure(self, fetch_history_id):
        pass


TEST_CONFIG = {
    'extraction_dir': '/tmp/tests/loader-tar/',  # where to extract the tarball
    'storage': {  # we instantiate it but we don't use it in test context
        'cls': 'remote',
        'args': {
            'url': 'http://127.0.0.1:9999',  # somewhere that does not exist
        }
    },
    'send_contents': False,
    'send_directories': False,
    'send_revisions': False,
    'send_releases': False,
    'send_occurrences': False,
    'content_packet_size': 100,
    'content_packet_block_size_bytes': 104857600,
    'content_packet_size_bytes': 1073741824,
    'directory_packet_size': 250,
    'revision_packet_size': 100,
    'release_packet_size': 100,
    'occurrence_packet_size': 100,
}


def parse_config_file(base_filename=None, config_filename=None,
                      additional_configs=None, global_config=True):
    return TEST_CONFIG


# Inhibit side-effect loading configuration from disk
TarLoader.parse_config_file = parse_config_file


class SWHTarLoaderNoStorage(LoaderNoStorageForTest, TarLoader):
    """A TarLoader with no persistence.

    Context:
        Load a tarball with a persistent-less tarball loader

    """
    pass


PATH_TO_DATA = '../../../../..'


class SWHTarLoaderITTest(TestCase):
    def setUp(self):
        super().setUp()

        self.loader = SWHTarLoaderNoStorage()

    @attr('fs')
    @istest
    def load(self):
        """Process a new tarball should be ok

        """
        # given
        start_path = os.path.dirname(__file__)
        tarpath = os.path.join(
            start_path, PATH_TO_DATA,
            'swh-storage-testdata/dir-folders/sample-folder.tgz')

        origin = {
            'url': 'file:///tmp/sample-folder',
            'type': 'dir'
        }

        visit_date = 'Tue, 3 May 2016 17:16:32 +0200'

        import datetime
        commit_time = int(datetime.datetime.now(
            tz=datetime.timezone.utc).timestamp()
        )

        swh_person = {
            'name': 'Software Heritage',
            'fullname': 'Software Heritage',
            'email': 'robot@softwareheritage.org'
        }

        revision_message = 'swh-loader-tar: synthetic revision message'
        revision_type = 'tar'
        revision = {
            'date': {
                'timestamp': commit_time,
                'offset': 0,
            },
            'committer_date': {
                'timestamp': commit_time,
                'offset': 0,
            },
            'author': swh_person,
            'committer': swh_person,
            'type': revision_type,
            'message': revision_message,
            'metadata': {},
            'synthetic': True,
        }

        occurrence = {
            'branch': os.path.basename(tarpath),
        }

        # when
        self.loader.load(tar_path=tarpath, origin=origin,
                         visit_date=visit_date, revision=revision,
                         occurrences=[occurrence])

        # then
        self.assertEquals(len(self.loader.all_contents), 8,
                          "8 contents: 3 files + 5 links")
        self.assertEquals(len(self.loader.all_directories), 6,
                          "6 directories: 4 subdirs + 1 empty + 1 main dir")
        self.assertEquals(len(self.loader.all_revisions), 1,
                          "synthetic revision")

        actual_revision = self.loader.all_revisions[0]
        self.assertTrue(actual_revision['synthetic'])
        self.assertEquals(actual_revision['parents'],
                          [])
        self.assertEquals(actual_revision['type'],
                          'tar')
        self.assertEquals(actual_revision['message'],
                          b'swh-loader-tar: synthetic revision message')
        self.assertEquals(actual_revision['directory'],
                          b'\xa7A\xfcM\x96\x8c{\x8e<\x94\xff\x86\xe7\x04\x80\xc5\xc7\xe5r\xa9')  # noqa

        self.assertEquals(
            actual_revision['metadata']['original_artifact'][0],
            {
                'sha1_git': 'cc848944a0d3e71d287027347e25467e61b07428',
                'archive_type': 'tar',
                'blake2s256': '5d70923443ad36377cd58e993aff0e3c1b9ef14f796c69569105d3a99c64f075',  # noqa
                'name': 'sample-folder.tgz',
                'sha1': '3ca0d0a5c6833113bd532dc5c99d9648d618f65a',
                'length': 555,
                'sha256': '307ebda0071ca5975f618e192c8417161e19b6c8bf581a26061b76dc8e85321d'  # noqa
            })

        self.assertEquals(len(self.loader.all_releases), 0)
        self.assertEquals(len(self.loader.all_occurrences), 1)
