# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest

from nose.tools import istest
from unittest.mock import patch

from swh.loader.tar import build


class TestBuildUtils(unittest.TestCase):
    @istest
    def compute_origin(self):
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
        self.assertEquals(actual_origin, expected_origin)

    @istest
    def _build_occurrence(self):
        # given
        expected_occurrence = {
            'branch': b'package-bar.tgz',
            'authority': 3,
            'validity': '2015-10-22 08:44:47.422384+00'
        }

        # when
        actual_occurrence = build._build_occurrence(
            b'/path/to/package-bar.tgz',
            authority_id=3,
            validity_ts=1445503487.4223838)

        # then
        self.assertEquals(actual_occurrence, expected_occurrence)

    @istest
    def compute_release__no_release(self):
        # given

        # when
        actual_release = build.compute_release(
            'pack-without-version.tgz',
            '/some/path/to/pack-without-version.tgz')

        # then
        self.assertIsNone(actual_release)

    @istest
    def compute_release(self):
        # given
        expected_release = {
            'name': '1.2.3rc1',
            'date': 'some-time',
            'offset': build.UTC_OFFSET,
            'author_name': '',
            'author_email': '',
            'comment': '',
        }

        # when
        with patch('swh.loader.tar.build._time_from_path',
                   return_value='some-time'):
            actual_release = build.compute_release(
                'foobar-1.2.3rc1.tgz',
                '/some/path/to/path-without-version.tgz')

        # then
        self.assertEquals(expected_release, actual_release)

    @istest
    def compute_revision(self):
        # when
        actual_revision = build.compute_revision()

        # then
        self.assertEquals(actual_revision, build.REVISION)
