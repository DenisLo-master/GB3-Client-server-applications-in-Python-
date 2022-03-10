import os.path
import unittest
# from unittest.mock import patch  # имитация действия функции sys запуск из терминала
import sys
from server import process_client_message

# sys.path.append(os.path.join(os.getcwd(), '..'))


class TestProcessClientMessage(unittest.TestCase):

    def test_structure_message(self):
        message = {'a': 1, 'b': 2}
        result = {'response': 400, 'error': 'Bad request'}
        self.assertEqual(result, process_client_message(message))

