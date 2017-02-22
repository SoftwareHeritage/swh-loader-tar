# Copyright (C) 2015  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest

from nose.tools import istest

from swh.loader.tar import utils


class TestUtils(unittest.TestCase):
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
