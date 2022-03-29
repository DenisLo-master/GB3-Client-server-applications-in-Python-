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
from errors import ReqFieldMissingError, NonDictInputError, IncorrectDataRecivedErrors
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
    LOGGER.debug(f'разбор сообщения от клиента {message}')
    if isinstance(message, dict):
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            LOGGER.debug(f'Код:200, сообщение от клиента - {message}')
            return {RESPONSE: 200}
        LOGGER.error(f'Код:400, структура сообщения не корректна - {message}')
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
    LOGGER.error(f'Код:400, не корректный тип сообщения - {message}')
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


def new_listen_socket(adress, port):
    # готовим сокет
    LOGGER.debug(f'Запуск сокета')
    sock = socket(AF_INET, SOCK_STREAM)
    LOGGER.debug(f'Установка параметров сокета')
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((adress, port))

    # слушаем порт на входящие подключения
    sock.listen(MAX_CONNECTION)
    LOGGER.info(f'Сервер {adress}:{port} запущен, ожидает подклчение клиентов')
    sock.settimeout(0.3)
    return sock


def main():
    LOGGER.info(f'Запуск сервера')
    try:
        listen_port = check_port()
        LOGGER.debug(f'Порт сервера определен')
    except IndexError:
        LOGGER.error('Не указан порт сервера, после параметра -p')
        sys.exit()
    except ValueError:
        LOGGER.error('Указан не корректный порт')
        sys.exit()

    try:
        listen_address = validation_address_ipv4(check_address())
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

    transport = new_listen_socket(listen_address, listen_port)
    clients = []

    while True:
        try:
            client_socket, client_address = transport.accept() #проверка подключений
        except OSError as e:
            pass
        else:
            LOGGER.info(f'Подключение клиента {client_address[0]}:{client_address[1]}')
            clients.append(client_socket)
        finally:
            #проверить наличие событий ввода-вывода без таймаута
            recv_data_lst = []
            send_data_lst = []
            try:

            try:
                message_from_client = get_message(client_socket)
                LOGGER.info(f'Получено сообщение от {client_address[0]}')
                response = process_client_message(message_from_client)
                send_message(client_socket, response)
                LOGGER.info(f'Cообщение для {client_address[0]} отправлено')
                client_socket.close()
                LOGGER.info(f'Сокет закрыт {client_address[0]}:{client_address[1]}')
            except json.JSONDecodeError:
                LOGGER.critical(f'Не удалось декодировать сообщение от клиента {client_address[0]}:{client_address[1]}')
                client_socket.close()
                LOGGER.info(f'Сокет закрыт {client_address[0]}:{client_address[1]}')
            except NonDictInputError:
                LOGGER.critical(f'Сообщение не является словарем')
                client_socket.close()
                LOGGER.info(f'Сокет закрыт {client_address[0]}:{client_address[1]}')


if __name__ == '__main__':
    main()

