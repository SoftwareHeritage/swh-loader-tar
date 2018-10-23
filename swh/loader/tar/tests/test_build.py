# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest
from unittest.mock import patch

from swh.loader.tar import build


class TestBuildUtils(unittest.TestCase):
    def test_compute_origin(self):
        # given
        expected_origin = {
            'url': 'rsync://some/url/package-foo',
            'type': 'rsync',
        }

        # when
        actual_origin = build.compute_origin(
            'rsync://some/url/',
            'rsync',
            '/some/root/path/',
            '/some/root/path/package-foo/package-foo-1.2.3.tgz')

        # then
        self.assertEqual(actual_origin, expected_origin)

    @patch('swh.loader.tar.build._time_from_path')
    def test_compute_revision(self, mock_time_from_path):
        mock_time_from_path.return_value = 'some-other-time'

        # when
        actual_revision = build.compute_revision('/some/path')

        expected_revision = {
            'date': {
                'timestamp': 'some-other-time',
                'offset': build.UTC_OFFSET,
            },
            'committer_date': {
                'timestamp': 'some-other-time',
                'offset': build.UTC_OFFSET,
            },
            'author': build.SWH_PERSON,
            'committer': build.SWH_PERSON,
            'type': build.REVISION_TYPE,
            'message': build.REVISION_MESSAGE,
        }

        # then
        self.assertEqual(actual_revision, expected_revision)

        mock_time_from_path.assert_called_once_with('/some/path')

    @patch('swh.loader.tar.build.os')
    def test_time_from_path_with_float(self, mock_os):
        class MockStat:
            st_mtime = 1445348286.8308342
        mock_os.lstat.return_value = MockStat()

        actual_time = build._time_from_path('some/path')

        self.assertEqual(actual_time, {
            'seconds': 1445348286,
            'microseconds': 8308342
        })

        mock_os.lstat.assert_called_once_with('some/path')

    @patch('swh.loader.tar.build.os')
    def test_time_from_path_with_int(self, mock_os):
        class MockStat:
            st_mtime = 1445348286

        mock_os.lstat.return_value = MockStat()

        actual_time = build._time_from_path('some/path')

        self.assertEqual(actual_time, {
            'seconds': 1445348286,
            'microseconds': 0
        })

        mock_os.lstat.assert_called_once_with('some/path')
