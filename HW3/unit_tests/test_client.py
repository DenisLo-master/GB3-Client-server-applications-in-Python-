import os.path
import unittest
from unittest.mock import patch  # имитация действия функции sys запуск из терминала
import sys
import client

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestCheckPort(unittest.TestCase):

    @patch.object(sys, 'argv', ['client.py', '-p'])
    def test_without_port_with_p(self):
        self.assertRaises(IndexError, client.check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 777])
    def test_with_wrong_port_min(self):
        self.assertRaises(ValueError, client.check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 98777])
    def test_with_wrong_port_max(self):
        self.assertRaises(ValueError, client.check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 'f45454'])
    def test_with_wrong_type_port_str(self):
        self.assertRaises(ValueError, client.check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 4.5454])
    def test_with_wrong_type_port_float(self):
        self.assertRaises(ValueError, client.check_port)


class TestCheckAddress(unittest.TestCase):

    def test_with_a_without_address(self):
        with patch.object(sys, 'argv', ['client.py', '-a']):
            self.assertRaises(IndexError, client.check_address)


class TestValidateAddress(unittest.TestCase):

    def test_wrong_delimetr_address(self):
        self.assertRaises(TypeError, client.validate_address, '127,0,0.1')

    def test_wrong_length_address_min(self):
        self.assertRaises(TypeError, client.validate_address, '401.0.1')

    def test_wrong_length_address_max(self):
        self.assertRaises(TypeError, client.validate_address, '401.0.1.2.5')

    def test_wrong_address(self):
        self.assertRaises(ValueError, client.validate_address, '401.0.0.1')

    def test_wrong_type_address(self):
        self.assertRaises(ValueError, client.validate_address, 'fd.0.0.1')


class TestCreatePresence(unittest.TestCase):

    def test_check_structure(self):
        template = ['action', 'time', 'user']
        self.assertCountEqual(template, client.create_presence().keys())

    def test_structure_account_name_in_user_presence(self):
        self.assertIn('account_name', client.create_presence()['user'].keys())

    def test_type_action_message(self):
        self.assertEqual('presence', client.create_presence()['action'])

    def test_format_time_presence(self):
        self.assertIsInstance(client.create_presence()['time'], float)

    def test_type_message(self):
        self.assertIsInstance(client.create_presence(), dict)


class TestProcessAnswer(unittest.TestCase):

    def test_wrong_message(self):
        message = {'a': 1, 'b': 2}
        self.assertRaises(ValueError, client.process_answer, message)

    def test_wrong_response_code(self):
        message = {'response': 1001}
        self.assertRaises(IndexError, client.process_answer, message)

    def test_response_message_correct(self):
        message = {'response': 200}
        self.assertEqual('200: OK', client.process_answer(message))

    def test_response_message_error(self):
        message = {'response': 400, 'error': 'Bad request'}
        self.assertEqual('400: Bad request', client.process_answer(message))