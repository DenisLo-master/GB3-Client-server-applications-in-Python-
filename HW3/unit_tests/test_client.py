import os.path
import unittest
from unittest.mock import patch  # имитация действия функции sys запуск из терминала
import sys
import client

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestStartClient(unittest.TestCase):

    @patch.object(sys, 'argv', ['client.py', '-p'])
    def test_run_client_without_port(self):
        self.assertRaises(IndexError, client.check_port)

    def test_run_client_with_wrong_port_min(self):
        with patch.object(sys, 'argv', ['client.py', '-p', 765]):
            with self.assertRaises(ValueError) as cm:
                client.check_port()
            self.assertTrue('В качестве порта укажите значение от 1024 до 65535' == cm.exception)
