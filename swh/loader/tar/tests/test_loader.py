# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os

from nose.plugins.attrib import attr

from swh.loader.core.tests import BaseLoaderTest, LoaderNoStorage
from swh.loader.tar.loader import TarLoader


class TarLoaderNoStorage(LoaderNoStorage, TarLoader):
    """A DirLoader with no persistence.

    Context:
        Load a tarball with a persistent-less tarball loader

    """
    def __init__(self, config={}):
        super().__init__(config=config)
        self.origin_id = 1
        self.visit = 1


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
    'send_snapshot': False,
    'content_packet_size': 100,
    'content_packet_block_size_bytes': 104857600,
    'content_packet_size_bytes': 1073741824,
    'directory_packet_size': 250,
    'revision_packet_size': 100,
    'release_packet_size': 100,
}


def parse_config_file(base_filename=None, config_filename=None,
                      additional_configs=None, global_config=True):
    return TEST_CONFIG


# Inhibit side-effect loading configuration from disk
TarLoader.parse_config_file = parse_config_file


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
        self.loader = TarLoaderNoStorage()

    @attr('fs')
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

        actual_revision = self.state('revision')[0]
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

        self.assertCountReleases(0)
        self.assertCountSnapshots(1)
