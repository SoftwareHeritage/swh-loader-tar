# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest
from unittest.mock import patch

from swh.loader.tar.tasks import LoadTarRepository


class TestTasks(unittest.TestCase):
    def test_check_task_name(self):
        task = LoadTarRepository()
        self.assertEqual(task.task_queue, 'swh_loader_tar')

    @patch('swh.loader.tar.loader.RemoteTarLoader.load')
    def test_task(self, mock_loader):
        mock_loader.return_value = {'status': 'eventful'}
        task = LoadTarRepository()

        # given
        actual_result = task.run_task(
            origin='origin', visit_date='visit_date',
            last_modified='last_modified')

        self.assertEqual(actual_result, {'status': 'eventful'})

        mock_loader.assert_called_once_with(
            origin='origin', visit_date='visit_date',
            last_modified='last_modified')
