# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

import pytest

from swh.model import hashutil

from swh.loader.core.tests import BaseLoaderTest
from swh.loader.tar.loader import TarLoader


TEST_CONFIG = {
    'extraction_dir': '/tmp/tests/loader-tar/',  # where to extract the tarball
    'storage': {  # we instantiate it but we don't use it in test context
        'cls': 'memory',
        'args': {
        }
    },
    'send_contents': True,
    'send_directories': True,
    'send_revisions': True,
    'send_releases': True,
    'send_snapshot': True,
    'content_packet_size': 100,
    'content_packet_block_size_bytes': 104857600,
    'content_packet_size_bytes': 1073741824,
    'directory_packet_size': 250,
    'revision_packet_size': 100,
    'release_packet_size': 100,
    'content_size_limit': 1000000000
}


class TestTarLoader(TarLoader):
    def parse_config_file(self, *args, **kwargs):
        return TEST_CONFIG


class TarLoaderTest(BaseLoaderTest):
    """Prepare the archive to load

    """
    def setUp(self):
        super().setUp('sample-folder.tgz',
                      start_path=os.path.dirname(__file__),
                      uncompress_archive=False)
        self.tarpath = self.destination_path


class TarLoaderTest1(TarLoaderTest):
    def setUp(self):
        super().setUp()
        self.loader = TestTarLoader()
        self.storage = self.loader.storage

    @pytest.mark.fs
    def test_load(self):
        """Process a new tarball should be ok

        """
        # given
        origin = {
            'url': 'file:///tmp/sample-folder',
            'type': 'dir'
        }

        visit_date = 'Tue, 3 May 2016 17:16:32 +0200'

        import datetime
        commit_time = int(datetime.datetime(
            2018, 12, 5, 13, 35, 23, 0,
            tzinfo=datetime.timezone(datetime.timedelta(hours=1))
        ).timestamp())

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
            'synthetic': True,
        }

        branch_name = os.path.basename(self.tarpath)

        # when
        self.loader.load(tar_path=self.tarpath, origin=origin,
                         visit_date=visit_date, revision=revision,
                         branch_name=branch_name)

        # then
        self.assertCountContents(8, "3 files + 5 links")
        self.assertCountDirectories(6, "4 subdirs + 1 empty + 1 main dir")
        self.assertCountRevisions(1, "synthetic revision")

        rev_id = hashutil.hash_to_bytes(
            '67a7d7dda748f9a86b56a13d9218d16f5cc9ab3d')
        actual_revision = next(self.storage.revision_get([rev_id]))
        self.assertTrue(actual_revision['synthetic'])
        self.assertEqual(actual_revision['parents'], [])
        self.assertEqual(actual_revision['type'], 'tar')
        self.assertEqual(actual_revision['message'],
                         b'swh-loader-tar: synthetic revision message')
        self.assertEqual(actual_revision['directory'],
                         b'\xa7A\xfcM\x96\x8c{\x8e<\x94\xff\x86\xe7\x04\x80\xc5\xc7\xe5r\xa9')  # noqa

        self.assertEqual(
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

        self.assertCountReleases(0)
        self.assertCountSnapshots(1)
