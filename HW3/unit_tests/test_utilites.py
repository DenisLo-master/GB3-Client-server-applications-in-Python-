import unittest
import sys
import os.path
from unittest.mock import patch  # имитация действия функции sys запуск из терминала
from common.utilites import check_port, check_address, validation_address_ipv4

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
        {'response': 400, 'error': 'Bad request'}
    }


if __name__ == '__main__':
    unittest.main()
