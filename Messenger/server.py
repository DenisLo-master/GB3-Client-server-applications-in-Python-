# клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
# реализованы в виде отдельных скриптов, содержащих соответствующие функции. Функции клиента: сформировать
# presence-сообщение; отправить сообщение серверу; получить ответ сервера; разобрать сообщение сервера; параметры
# командной строки скрипта client.py <addr> [<port>]: addr — ip-адрес сервера; (по умолчанию 127.0.0.1); port —
# tcp-порт на сервере, (по умолчанию 7777). Функции сервера: принимает сообщение клиента; формирует ответ клиенту;
# отправляет ответ клиенту; имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию
# использует 7777); -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).

import sys
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4
import json
import logging
import logs_config.server_log_config

LOGGER = logging.getLogger('server')

def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь ответ для клиента
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от клиента {message}')
    if isinstance(message, dict):
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            LOGGER.debug(f'Код:200, сообщение от клиента - {message}')
            return {RESPONSE: 200}
        LOGGER.error(f'Код:400, структура сообщения не корректно - {message}')
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
    LOGGER.error(f'Код:400, не корректный тип сообщения - {message}')
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


def main():
    LOGGER.info(f'запуск сервера')
    try:
        listen_port = check_port()
        LOGGER.debug(f'порт сервера определен')
    except IndexError:
        LOGGER.error('После параметра -\'p\' необходимо указать номер порта для подключения')
        sys.exit('После параметра -\'p\' необходимо указать номер порта для подключения')
    except ValueError:
        LOGGER.error('В качестве порта укажите значение от 1024 до 65535')
        sys.exit('В качестве порта укажите значение от 1024 до 65535')

    try:
        listen_address = validation_address_ipv4(check_address())
        LOGGER.debug(f'адрес сервера определен')
    except IndexError:
        LOGGER.error('не указан IP сервераэ, после -a')
        sys.exit('После параметра -\'a\' можно указать IP адрес сервера')
    except TypeError:
        LOGGER.error('IP адрес указан не правильно')
        sys.exit('IP адрес указан не правильно, запишите в формате 0.0.0.0')
    except ValueError:
        LOGGER.error('указан некорректный IP адрес сервера')
        sys.exit('указан некорректный IP адрес сервера')

    # готовим сокет
    LOGGER.debug(f'запуск сокета')
    transport = socket(AF_INET, SOCK_STREAM)
    LOGGER.debug(f'установка параметров сокета')
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    # слушаем порт на входящие подключения
    transport.listen(MAX_CONNECTION)
    LOGGER.info(f'сервер {listen_address}:{listen_port} запущен, ожидает подклчение клиентов')

    while True:
        client_socket, client_address = transport.accept()
        LOGGER.info(f'подключение клиента {client_address[0]}:{client_address[1]}')
        try:
            message_from_client = get_message(client_socket)
            LOGGER.info(f'Получено сообщение от {client_address[0]}')
            response = process_client_message(message_from_client)
            send_message(client_socket, response)
            LOGGER.info(f'Cообщение для {client_address[0]} отправлено')
            client_socket.close()
            LOGGER.info(f'Сокет закрыт {client_address[0]}:{client_address[1]}')
        except (ValueError, json.JSONDecodeError):
            LOGGER.error(f'Получено не корректное сообщение от клиента {client_address[0]}:{client_address[1]}')
            client_socket.close()
            LOGGER.info(f'Сокет закрыт {client_address[0]}:{client_address[1]}')


if __name__ == '__main__':
    main()

