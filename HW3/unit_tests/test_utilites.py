import json
import unittest
import sys
import os.path
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from unittest.mock import patch  # имитация действия функции sys запуск из терминала
from common.utilites import check_port, check_address, validation_address_ipv4, get_message, send_message
from common.variables import ENCODING, MAX_PACKAGE_LENGTH

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestCheckPort(unittest.TestCase):

    @patch.object(sys, 'argv', ['client.py', '-p'])
    def test_without_port_with_p(self):
        """Тест исключения, с указанным параметром -p, но без введенного порта"""
        self.assertRaises(IndexError, check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 777])
    def test_with_wrong_port_min(self):
        """Тест исключения, указан порт ниже допустимого диапазона"""
        self.assertRaises(ValueError, check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 98777])
    def test_with_wrong_port_max(self):
        """Тест исключения, указан порт выше допустимого диапазона"""
        self.assertRaises(ValueError, check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 'f45454'])
    def test_with_wrong_type_port_str(self):
        """Тест исключения, указано НЕкорректное значение порта, тип str"""
        self.assertRaises(ValueError, check_port)

    @patch.object(sys, 'argv', ['client.py', '-p', 4.5454])
    def test_with_wrong_type_port_float(self):
        """Тест исключения, указано НЕкорректное значение порта, тип float"""
        self.assertRaises(ValueError, check_port)


class TestCheckAddress(unittest.TestCase):

    def test_with_a_without_address(self):
        """Тест исключения, с указанным параметром -a, но без введенного ip адреса"""
        with patch.object(sys, 'argv', ['client.py', '-a']):
            self.assertRaises(IndexError, check_address)


class TestValidateAddress(unittest.TestCase):

    def test_wrong_delimetr_address(self):
        """Тест исключения, указан ip адрес с НЕкорректным разделителем"""
        self.assertRaises(TypeError, validation_address_ipv4, '127,0,0.1')

    def test_wrong_length_address_min(self):
        """Тест исключения, указано НЕкорректное значение ip адреса, по количеству групп - 3"""
        self.assertRaises(TypeError, validation_address_ipv4, '401.0.1')

    def test_wrong_length_address_max(self):
        """Тест исключения, указано НЕкорректное значение ip адреса, по количеству групп - 5"""
        self.assertRaises(TypeError, validation_address_ipv4, '127.0.1.2.5')

    def test_wrong_address(self):
        """Тест исключения, указано НЕкорректное значение ip адреса"""
        self.assertRaises(ValueError, validation_address_ipv4, '401.0.0.1')

    def test_wrong_type_address(self):
        """Тест исключения, указано НЕкорректный тип значений ip адреса"""
        self.assertRaises(ValueError, validation_address_ipv4, 'fd.0.0.1')


class TestConnection(unittest.TestCase):
    test_message = {
        'action': 'presence',
        'time': 1234.4343523,
        'user': {
            'account_name': 'Guest'
        },
    }

    response_200 = {
        'response': 200,
    }

    response_400 = {
        'response': 400,
        'error': 'Bad request'
    }

    def setUp(self):
        self.s_socket = socket(AF_INET, SOCK_STREAM)
        self.s_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_socket.bind(('127.0.0.1', 7777))
        self.s_socket.listen(1)

        self.c_socket = socket(AF_INET, SOCK_STREAM)
        self.c_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.c_socket.connect(('127.0.0.1', 7777))
        self.sc_socket, self.sc_address = self.s_socket.accept()

    def tearDown(self):
        self.s_socket.close()
        self.c_socket.close()
        self.sc_socket.close()

    def test_send_message_client_server(self):
        """Проверка отправки коррекктного сообщения, сравниваем до и после"""
        send_message(self.c_socket, self.test_message)
        self.c_socket.close()
        test_response = self.sc_socket.recv(MAX_PACKAGE_LENGTH)
        test_response = json.loads(test_response.decode(ENCODING))
        self.sc_socket.close()
        self.assertEqual(self.test_message, test_response)

    def test_get_message_client_server(self):
        """Проверка получения коррекктного сообщения, сравниваем до и после"""
        j_message = json.dumps(self.test_message)
        self.c_socket.send(j_message.encode(ENCODING))
        self.c_socket.close()
        response = get_message(self.sc_socket)
        self.assertEqual(self.test_message, response)

    def test_get_message_400(self):
        """Проверка корректной расшифровки ошибочного словаря"""
        j_response = json.dumps(self.response_400)
        self.sc_socket.send(j_response.encode(ENCODING))
        self.sc_socket.close()
        response = get_message(self.c_socket)
        self.assertEqual(self.response_400, response)

    def test_get_message_200(self):
        """Проверка корректной расшифровки корректного словаря"""
        j_response = json.dumps(self.response_200)
        self.sc_socket.send(j_response.encode(ENCODING))
        self.sc_socket.close()
        response = get_message(self.c_socket)
        self.assertEqual(self.response_200, response)

    def test_send_wrong_message(self):
        """Тест исключеения, если объект на получение не словарь"""
        self.assertRaises(TypeError, send_message, self.sc_socket, 'no dict')

    def test_get_message_not_dict(self):
        """Тест исключеения, если объект на получение не словарь"""
        j_message = json.dumps('not dict')
        self.sc_socket.send(j_message.encode(ENCODING))
        self.sc_socket.close()
        self.assertRaises(TypeError, get_message, self.c_socket)

    def test_get_response_dict(self):
        """Тест исключеения, если объект на получение словарь"""
        j_message = json.dumps(self.response_200)
        self.sc_socket.send(j_message.encode(ENCODING))
        self.sc_socket.close()
        self.assertIsInstance(get_message(self.c_socket), dict)


if __name__ == '__main__':
    unittest.main()
