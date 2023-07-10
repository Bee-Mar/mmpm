#!/usr/bin/env python3
from mmpm.magicmirror.controller import MagicMirrorController
import unittest
from unittest.mock import patch, MagicMock
from tests.helpers import MockedMMPMEnv
import shutil
from faker import Faker

fake = Faker()

class MagicMirrorControllerTests(unittest.TestCase):

    def setUp(self):
        self.controller = MagicMirrorController()
        self.controller.env = MockedMMPMEnv()
        self.controller.env.mmpm_magicmirror_root.get().mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.controller.env.mmpm_magicmirror_root.get())

    #FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_start_with_pm2(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.return_value = True
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = 'magicmirror'
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = None

    #    result = self.controller.start()

    #    self.assertTrue(mock_run_cmd.called)
    #    self.assertEqual(result, True)

    #FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_start_with_docker_compose(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.side_effect = [None, True]
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = None
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = 'docker-compose.yml'

    #    result = self.controller.start()

    #    self.assertTrue(mock_run_cmd.called)
    #    self.assertEqual(result, True)

    @patch('mmpm.magicmirror.controller.shutil.which')
    @patch('mmpm.magicmirror.controller.run_cmd')
    def test_start_with_npm(self, mock_run_cmd, mock_shutil_which):
        mock_shutil_which.side_effect = [None, None]
        self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = None
        self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = None

        result = self.controller.start()

        self.assertTrue(mock_run_cmd.called)
        self.assertEqual(result, True)

    # FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_start_no_command(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.side_effect = [None, None]
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = None
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = None

    #    result = self.controller.start()

    #    self.assertFalse(mock_run_cmd.called)
    #    self.assertEqual(result, False)

    #FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_stop_with_pm2(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.return_value = True
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = 'magicmirror'
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = None

    #    result = self.controller.stop()

    #    self.assertTrue(mock_run_cmd.called)
    #    self.assertEqual(result, True)

    #FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_stop_with_docker_compose(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.side_effect = [None, True]
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = None
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = 'docker-compose.yml'

    #    result = self.controller.stop()

    #    self.assertTrue(mock_run_cmd.called)
    #    self.assertEqual(result, True)

    #FIXME
    #@patch('mmpm.magicmirror.controller.shutil.which')
    #@patch('mmpm.magicmirror.controller.run_cmd')
    #def test_stop_no_command(self, mock_run_cmd, mock_shutil_which):
    #    mock_shutil_which.side_effect = [None, None]
    #    self.controller.env.mmpm_magicmirror_pm2_process_name.get.return_value = None
    #    self.controller.env.mmpm_magicmirror_docker_compose_file.get.return_value = None

    #    result = self.controller.stop()

    #    self.assertFalse(mock_run_cmd.called)
    #    self.assertEqual(result, False)

    def test_restart(self):
        with patch.object(self.controller, 'stop') as mock_stop:
            with patch.object(self.controller, 'start') as mock_start:
                self.controller.restart()
                mock_stop.assert_called_once()
                mock_start.assert_called_once()

    @patch('mmpm.magicmirror.controller.get_pids')
    def test_is_running_true(self, mock_get_pids):
        mock_get_pids.return_value = [fake.pyint()]
        result = self.controller.is_running()
        self.assertTrue(result)

    @patch('mmpm.magicmirror.controller.get_pids')
    def test_is_running_false(self, mock_get_pids):
        mock_get_pids.return_value = []
        result = self.controller.is_running()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

