import os.path
import unittest
import sys
from client import create_presence, process_answer

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestCreatePresence(unittest.TestCase):

    def test_check_template(self):
        """Тест соответствия шаблону сообщения по ключам"""
        template = ['action', 'time', 'user']
        self.assertCountEqual(template, create_presence().keys())

    def test_structure_account_name_in_user(self):
        """Тест наличия словаря {ACCOUNT_NAME: account_name} для ключа USER"""
        self.assertIn('account_name', create_presence()['user'].keys())

    def test_type_action_message(self):
        """Тест соответвия типа сообщения 'presence' по ключу 'action' """
        self.assertEqual('presence', create_presence()['action'])

    def test_format_time_presence(self):
        """Тест соответствия формата времени в ключе time """
        self.assertIsInstance(create_presence()['time'], float)

    def test_type_message(self):
        """Тест корректного вывода сообщения, в виде словаря"""
        self.assertIsInstance(create_presence(), dict)


class TestProcessAnswer(unittest.TestCase):

    def test_wrong_message(self):
        """Тест исключения, на вход НЕкорректная структура сообщения"""
        message = {'a': 1, 'b': 2}
        self.assertRaises(ValueError, process_answer, message)

    def test_wrong_response_code(self):
        """Тест исключения, неизвествного кода ошибки 1001, полученного от сервера"""
        message = {'response': 1001}
        self.assertRaises(IndexError, process_answer, message)

    def test_response_message_correct(self):
        """Тест корректного разбора ответа 200 полученного от сервера"""
        message = {'response': 200}
        self.assertEqual('200: OK', process_answer(message))

    def test_response_message_error(self):
        """Тест корректного разбора ответа 400 полученного от сервера, сообщение на вход в виде str"""
        message = {'response': 400, 'error': 'Bad request'}
        self.assertEqual('400: Bad request', process_answer(message))

    def test_response_wront_type_str_message(self):
        """Тест исключения, на вход НЕкорректный тип сообщения, тип str"""
        message = 'abc'
        self.assertRaises(TypeError, process_answer, message)

    def test_response_wront_type_list_message(self):
        """Тест исключения, на вход НЕкорректный тип сообщения, тип list"""
        message = ['action', 'asd']
        self.assertRaises(TypeError, process_answer, message)


# class TestConnection(unittest.TestCase):


if __name__ == '__main__':
    unittest.main()
