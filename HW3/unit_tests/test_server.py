import os.path
import unittest
import sys
from server import process_client_message
from client import create_presence

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestProcessClientMessage(unittest.TestCase):

    def test_type_response_from_wrong_message(self):
        """Тест корректного вывода, в виде словаря, сообщение на вход в виде НЕкорректного словаря"""
        message = {'a': 1, 'b': 2}
        self.assertIsInstance(process_client_message(message), dict)

    def test_400_validation_wrong_message(self):
        """Тест корректного разбора ответа 400, сообщение на вход в виде НЕкорректного словаря"""
        message = {'a': 1, 'b': 2}
        result = {'response': 400, 'error': 'Bad request'}
        self.assertEqual(result, process_client_message(message))

    def test_400_wrong_type_list_message(self):
        """Тест корректного разбора ответа 400, сообщение на вход в виде list"""
        message = ['action', 'time', 'user']
        result = {'response': 400, 'error': 'Bad request'}
        self.assertEqual(result, process_client_message(message))

    def test_400_wrong_type_str_message(self):
        """Тест корректного разбора ответа 400, сообщение на вход в виде str"""
        message = 'abc'
        result = {'response': 400, 'error': 'Bad request'}
        self.assertEqual(result, process_client_message(message))

    def test_type_response_from_right_message(self):
        """Тест корректного вывода, в виде словаря, сообщение на вход в виде корректного словаря"""
        message = create_presence()
        self.assertIsInstance(process_client_message(message), dict)

    def test_200_validation_right_message(self):
        """Тест корректного разбора ответа 200, сообщение на вход в виде корректного словаря"""
        message = create_presence()
        result = {'response': 200}
        self.assertEqual(result, process_client_message(message))


if __name__ == '__main__':
    unittest.main()
