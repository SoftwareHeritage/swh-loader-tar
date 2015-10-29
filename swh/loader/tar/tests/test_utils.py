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
            'gnunet-java-0.9.4.jar': ('gnunet-java-', '0.9.4', '.jar'),
            'pycdio-0.15-py2.5-linux-i686.egg': (
                'pycdio-', '0.15-py2.5-linux-i686', '.egg'),
            'rbcdio-0.04.gem': ('rbcdio-', '0.04', '.gem'),
            'librejs-6.0.5.xpi': ('librejs-', '6.0.5', '.xpi'),
            'icecat-31.8.0.csb.langpack.xpi': (
                'icecat-', '31.8.0.csb.langpack', '.xpi'),
            'icecatmobile-31.8.0.en-US.android-arm.apk': (
                'icecatmobile-', '31.8.0.en-US.android-arm', '.apk'),
            'icecat-31.8.0.en-US.mac.dmg': (
                'icecat-', '31.8.0.en-US.mac', '.dmg'),
            'gnutls-3.0.21-1gn.DevPak': ('gnutls-', '3.0.21-1gn', '.DevPak'),

            # . separator
            'greg-1.4.tar.gz': ('greg-', '1.4', '.tar.gz'),

            # number in software product
            'aspell6-pt_BR-20070411-0.tar.bz2': (
                'aspell6-pt_BR-', '20070411-0', '.tar.bz2'),
            'libosip2-3.3.0.tar.gz': ('libosip2-', '3.3.0', '.tar.gz'),

            # other cases
            'hurd-F2-main.iso': ('hurd-F2-main', None, '.iso'),

            'winboard-4_0_5.exe': ('winboard-', '4_0_5', '.exe'),

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

        cls.files_error = ['.tar', '.anything']

    @istest
    def parse_filename(self):
        for f in self.files:
            # when
            actual_components = utils.parse_filename(f)

            # then
            name, version, ext = self.files[f]
            expected_components = {
                'software_name': name,
                'release_number': version,
                'extension': ext,
            }

            self.assertEquals(actual_components, expected_components)

    @istest
    def parse_filename_not_parseable_file(self):
        for f in self.files_error:
            with self.assertRaises(ValueError):
                utils.parse_filename(f)

    @istest
    def release_number(self):
        for f in self.files.keys():
            # when
            actual_ext = utils.release_number(f)

            # then
            _, expected_rel_num, _ = self.files[f]
            self.assertEquals(
                actual_ext,
                expected_rel_num,
                'for %s, the version should be %s' % (f, expected_rel_num))

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

    @istest
    def convert_to_hex(self):
        # given
        input_dict = {
            'sha1_git': b'\xf6\xb7 \x8b+\xcd \x9fq5E\xe6\x03\xffg\x87\xd7\xb9D\xa1',  # noqa
            'sha1': b'\xf4O\xf0\xd4\xc0\xb0\xae\xca\xe4C\xab%\x10\xf7\x12h\x1e\x9f\xac\xeb',  # noqa
            'sha256': b'\xa8\xf9=\xf3\xfek\xa2$\xee\xc7\x1b\xc2\x83\xca\x96\xae8\xaf&\xab\x08\xfa\xb1\x13\xec(.s]\xf6Yb'}  # noqa

        expected_dict = {'sha1_git': 'f6b7208b2bcd209f713545e603ff6'
                                     '787d7b944a1',
                         'sha1': 'f44ff0d4c0b0aecae443ab2510f712681e'
                                 '9faceb',
                         'sha256': 'a8f93df3fe6ba224eec71bc283ca96ae3'
                                   '8af26ab08fab113ec282e735df65962'}

        # when
        actual_dict = utils.convert_to_hex(input_dict)

        # then
        self.assertDictEqual(actual_dict, expected_dict)

    @istest
    def convert_to_hex_edge_cases(self):
        # when
        actual_dict = utils.convert_to_hex({})
        # then
        self.assertDictEqual(actual_dict, {})

        self.assertIsNone(utils.convert_to_hex(None))
