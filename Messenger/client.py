import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4
from common.variables import ACTION, ACCOUNT_NAME, PRESENCE, RESPONSE, TIME, USER, ERROR
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


def main():
    LOGGER.info(f'Запуск клиента')
    try:
        server_port = check_port()
        LOGGER.debug(f'Порт сервера определен')
    except IndexError:
        LOGGER.error('Не указан порт сервера, после параметра -p')
        sys.exit()
    except ValueError:
        LOGGER.error('Указан не корректный порт')
        sys.exit()

    try:
        server_address = validation_address_ipv4(check_address())
        LOGGER.debug(f'Адрес сервера определен')
    except IndexError:
        LOGGER.error('Не указан IP сервера, после параметра -a')
        sys.exit()
    except TypeError:
        LOGGER.error('IP адрес указан не правильно')
        sys.exit()
    except ValueError:
        LOGGER.error('Указан некорректный IP адрес сервера')
        sys.exit()

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
    try:
        LOGGER.info(f'Ожидание ответа от сервера {server_address}:{server_port}: ')
        process_answer(get_message(transport))
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except json.JSONDecodeError:
        LOGGER.critical(f'Не удалось декодировать сообщение от сервера')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except IncorrectDataRecivedErrors:
        LOGGER.critical(f'Некорректное сообщение от сервера {server_address}:{server_port}')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except NonDictInputError:
        LOGGER.critical(f'сообщение от сервера {server_address}:{server_port} не является словарем')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')
    except ReqFieldMissingError:
        LOGGER.critical(f'отсутствует обязательное поле в сообщении от сервера {server_address}:{server_port}')
        transport.close()
        LOGGER.info(f'Сокет закрыт {server_address}:{server_port}')

if __name__ == '__main__':
    main()
