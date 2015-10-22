# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest

from nose.tools import istest

from swh.loader.tar import utils


class TestUtils(unittest.TestCase):
    @classmethod
    def setupClass(cls):
        cls.files = {
            'free-ipmi-1.2.2.tar': ('free-ipmi-', '1.2.2', '.tar'),
            'free-ipmi-1.2.2.tar.gz': ('free-ipmi-', '1.2.2', '.tar.gz'),
            'free-ipmi-1.2.2.tar.tgz': ('free-ipmi-', '1.2.2', '.tar.tgz'),
            'gcc-testsuite-4.4.2-4.4.3.diff.bz2': (
                'gcc-testsuite-', '4.4.2-4.4.3', '.diff.bz2'),
            'gcc-java-4.0.4.tar.gz': ('gcc-java-', '4.0.4', '.tar.gz'),
            'gmp-2.0.tar.lzma': ('gmp-', '2.0', '.tar.lzma'),
            'win-gerwin-0.6.zip': ('win-gerwin-', '0.6', '.zip'),
            'ballandpaddle-0.8.0.tar.xz': (
                'ballandpaddle-', '0.8.0', '.tar.xz'),
            'mail-1.1.1.some.lz': ('mail-', '1.1.1.some', '.lz'),
            'gmp-4.1.1-4.1.2.diff.tar.Z': (
                'gmp-', '4.1.1-4.1.2', '.diff.tar.Z'),
            'findutils-4.2.18.tar.bzip2': (
                'findutils-', '4.2.18', '.tar.bzip2'),

            # . separator
            'greg-1.4.tar.gz': ('greg-', '1.4', '.tar.gz'),

            # number in software product
            'aspell6-pt_BR-20070411-0.tar.bz2': (
                'aspell6-pt_BR-', '20070411-0', '.tar.bz2'),
            'libosip2-3.3.0.tar.gz': ('libosip2-', '3.3.0', '.tar.gz'),

            # particular patterns...
            'gift-0.1.9+3epsilon.tar.gz': (
                'gift-', '0.1.9+3epsilon', '.tar.gz'),
            'gift-0.1.6pre2.tgz': ('gift-', '0.1.6pre2', '.tgz'),
            'binutils-2.19.1a.tar.bz2': ('binutils-', '2.19.1a', '.tar.bz2'),
            'readline-4.2-4.2a.diff.gz': ('readline-', '4.2-4.2a', '.diff.gz'),

            # with arch patterns
            'cvs-1.12.6-BSD.bin.gz': ('cvs-', '1.12.6-BSD.bin', '.gz'),
            'cvs-1.12.12-SunOS-5.8-i386.gz': (
                'cvs-', '1.12.12-SunOS-5.8-i386', '.gz'),
            'gnutls-3.0.20-w32.zip': ('gnutls-', '3.0.20-w32', '.zip'),
            'mit-scheme_7.7.90+20080130-0gutsy1.diff.gz': (
                'mit-scheme_', '7.7.90+20080130-0gutsy1', '.diff.gz'),

            # no release number
            'gnu.ps.gz': ('gnu', None, '.ps.gz'),
            'direvent-latest.tar.gz': ('direvent-latest', None, '.tar.gz'),
        }

    @istest
    def release_number(self):
        for f in self.files:
            # when
            actual_rel_num = utils.release_number(f)

            # then
            _, expected_rel_num, _ = self.files[f]
            self.assertEquals(
                actual_rel_num,
                expected_rel_num,
                'for %s, the version should be %s' % (f, expected_rel_num))

    @istest
    def extension(self):
        for f in self.files.keys():
            # when
            actual_ext = utils._extension(f)

            # then
            _, _, expected_ext = self.files[f]
            self.assertEquals(
                actual_ext,
                expected_ext,
                'for %s, the extension should be %s' % (f, expected_ext))

    @istest
    def software_name(self):
        for f in self.files.keys():
            # when
            actual_name = utils._software_name(f)

            # then
            expected_name, _, _ = self.files[f]
            self.assertEquals(
                actual_name,
                expected_name,
                'for %s, the name should be %s' % (f, expected_name))

    @istest
    def commonname(self):
        # when
        actual_commonname = utils.commonname('/some/where/to/',
                                             '/some/where/to/go/to')
        # then
        self.assertEquals('go/to', actual_commonname)

        # when
        actual_commonname2 = utils.commonname(b'/some/where/to/',
                                              b'/some/where/to/go/to')
        # then
        self.assertEquals(b'go/to', actual_commonname2)
