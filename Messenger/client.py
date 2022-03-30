import sys
import time
import argparse
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4
from common.variables import ACTION, ACCOUNT_NAME, PRESENCE, RESPONSE, TIME, USER, ERROR, MESSAGE, \
    MESSAGE_TEXT, SENDER, DEFAULT_PORT, DEFAULT_IP_ADDRESS
import json
from errors import ReqFieldMissingError, NonDictInputError, IncorrectDataRecivedErrors
import logging
import logs_config.client_log_config


LOGGER = logging.getLogger('client')


def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутсвии клиента
    : param account_name:
    :return:
    """
    LOGGER.debug(f'Подготовка сообщения для сервера от пользователя {account_name}')
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
    }
    LOGGER.debug(f'Сообщения для сервера подготовлено {message}')
    return message


def create_message(client_socket, account_name='Guest'):
    """
    Функция обрабатые ввод польователя: завершение работы или генерация сообщения для отправки на сервер
    :param client_socket:
    :return:
    """
    input_message = input('Введите сообщение для отправки или "!!!" для выхода:\n')
    LOGGER.debug(f'Введенное сообщение от пользователя {input_message}')
    if input_message == '!!!':
        client_socket.close()
        LOGGER.info(f'Пользователь {account_name} завершил работу')
        print('Спасибо за использование нашего сервиса')
        sys.exit(0)
    LOGGER.debug(f'Подготовка сообщения для сервера от пользователя {account_name}')
    message = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        MESSAGE_TEXT: input_message
    }
    LOGGER.debug(f'Сообщения для сервера подготовлено {message}')
    return message


def process_answer(message):
    """
    Функция разирает ответ сервера
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от сервера {message}')
    if isinstance(message, dict):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                LOGGER.info(f'Код:200, ОК')
                return 'Код:200, ОК'
            elif message[RESPONSE] == 400:
                LOGGER.critical(f'Код:400, {message[ERROR]}')
                return
            else:
                raise IncorrectDataRecivedErrors
        raise ReqFieldMissingError
    raise NonDictInputError


def message_from_server(message):
    """
    Функция - обработчик сообщений других пользователей, поступающих с сервера
    :param message:
    :return:
    """
    if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] != '' and MESSAGE_TEXT in message:
        print(f' сообщение от{message[USER][ACCOUNT_NAME]}:\n'
              f'{message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


def arg_parser():
    """
    Создаем парсер аргументов командной строки и читаем параметры
    :return:
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('-p', '--port', default=DEFAULT_PORT, nargs='?')
        parser.add_argument('-m', '--mode', default='listen', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = int(namespace.port)
        client_mode = namespace.mode

        # проверка номера порта
        if not 1023 < server_port < 65535:
            LOGGER.critical(f'Попытка запустить клиента с неподходящим номером порта:{server_port}'
                            f'Допустимы адреса с 1024 до 65535. Клиент завершается')
            sys.exit(1)

        # проверка допустимого режима работы
        if client_mode not in ('listen', 'send'):
            raise ValueError
        return server_address, server_port, client_mode
    except ValueError:
        LOGGER.critical(f'Указан недопустимый режим работы {client_mode},'
                        f'допустимые режимы: listen, send')
        sys.exit(1)


def main():
    LOGGER.info(f'Запуск клиента')

    server_address, server_port, client_mode = arg_parser()

    try:
        # готовим сокет
        LOGGER.debug(f'Запуск сокета')
        transport = socket(AF_INET, SOCK_STREAM)
        LOGGER.debug(f'Установка параметров сокета')
        transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # подключение к серверу
        transport.connect((server_address, server_port))
        LOGGER.info(f'Подключение к серверу: {server_address}:{server_port}')
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        LOGGER.debug(f'Сообщение отправлено к серверу: {server_address}:{server_port}')
        LOGGER.info(f'Ожидание ответа от сервера {server_address}:{server_port}: ')
        process_answer(get_message(transport))
    except json.JSONDecodeError:
        LOGGER.critical(f'Не удалось декодировать сообщение от сервера')
        transport.close(1)
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except IncorrectDataRecivedErrors:
        LOGGER.critical(f'Некорректное сообщение от сервера {server_address}:{server_port}')
        transport.close(1)
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except NonDictInputError:
        LOGGER.critical(f'сообщение от сервера {server_address}:{server_port} не является словарем')
        transport.close(1)
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except ReqFieldMissingError:
        LOGGER.critical(f'отсутствует обязательное поле в сообщении от сервера {server_address}:{server_port}')
        transport.close(1)
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось пожключиться к серверу {server_address}:{server_port},'
                        f'конечный компьютер отверг запрос на подключение')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
        sys.exit(1)

    # Если соединение с сервером установлено корректно,
    # начинаем обмен с ним, согласно режиму client_mode.
    # основной цикл программы
    if client_mode == 'send':
        print('Режим работы - отправка сообщений')
    else:
        print('Режим работы - приём сообщений')
    while True:
        # режим работы - отправка сообщений
        if client_mode == 'send':
            try:
                send_message(transport, create_message(transport))
            except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                LOGGER.error(f'Соединение с сервером {server_address}:{server_port} было потеряно')
                sys.exit(1)
        # режим работы - прием сообщений
        if client_mode == 'listen':
            try:
                message_from_server(get_message(transport))
            except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                LOGGER.error(f'Соединение с сервером {server_address}:{server_port} было потеряно')
                sys.exit(1)


if __name__ == '__main__':
    main()
