# клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
# реализованы в виде отдельных скриптов, содержащих соответствующие функции. Функции клиента: сформировать
# presence-сообщение; отправить сообщение серверу; получить ответ сервера; разобрать сообщение сервера; параметры
# командной строки скрипта client.py <addr> [<port>]: addr — ip-адрес сервера; (по умолчанию 127.0.0.1); port —
# tcp-порт на сервере, (по умолчанию 7777). Функции сервера: принимает сообщение клиента; формирует ответ клиенту;
# отправляет ответ клиенту; имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию
# использует 7777); -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
import argparse
import sys
import select
import json
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR, MESSAGE, MESSAGE_TEXT, EXIT,SENDER
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4
from errors import ReqFieldMissingError, NonDictInputError, IncorrectDataRecivedErrors
import logging
import logs_config.server_log_config

LOGGER = logging.getLogger('server')


def process_client_message(message, client, messages_order):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь ответ для клиента
    :param message:
    :return:
    """
    LOGGER.debug(f'разбор сообщения от клиента {get_ip_client(client)}')
    if isinstance(message, dict):
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] != '':
            LOGGER.debug(f'Код:200, сообщение PRESENSE от клиента - {message}')
            send_message(client, {RESPONSE: 200})
            return
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] != '' and MESSAGE_TEXT in message:
            LOGGER.debug(f'Код:200, сообщение TEXT_MESSAGE от клиента - {message}')
            messages_order[client] = message
            return messages_order
        # client_exit(message)
        else:
            LOGGER.error(f'Код:400, структура сообщения от клиента {get_ip_client(client)} не корректна - {message}')
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad request'
            })
            return
    else:
        LOGGER.error(f'Код:400, от клиента {get_ip_client(client)} не корректный тип сообщения - {message}')
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad request'
        })
        return


def get_ip_client(client_socket):
    """
    Получение адреса и порт клиента из сокета
    :param client_socket:
    :return: client
    """
    client = f'{client_socket.getsockname()[0]}:{client_socket.getsockname()[1]}'
    return client


def new_listen_socket(adress, port):
    """
    Подготовка сокета на сервере
    :param adress:
    :param port:
    :return: sock
    """
    # готовим сокет
    LOGGER.debug(f'Запуск сокета')
    sock = socket(AF_INET, SOCK_STREAM)
    LOGGER.debug(f'Установка параметров сокета')
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((adress, port))

    # слушаем порт на входящие подключения
    sock.listen(MAX_CONNECTION)
    LOGGER.info(f'Сервер {adress}:{port} запущен, ожидает подклчение клиентов')
    sock.settimeout(0.2)
    return sock


def send_message_for_waiting(message, send_data_lst):
    """
    Отправка сообщения всем клиентам
    :param message:
    :param send_data_lst:
    :return:
    """
    for waiting_client in send_data_lst:
        try:
            send_message(waiting_client, message)
            LOGGER.info(f'Cообщение для {get_ip_client(waiting_client)} отправлено')
        except:
            LOGGER.info(f'Клиент  {get_ip_client(waiting_client)} отключился от сервера')
            waiting_client.close()
            LOGGER.info(f'Сокет клиента {get_ip_client(waiting_client)} закрыт')
            send_data_lst.remove(waiting_client)
            LOGGER.debug(f'Клиент {get_ip_client(waiting_client)} удален из списка получателей сообщений')


def recv_message_from_clients(recv_data_lst, messages_order, clients_list):
    """
    Каждое сообщения из recv_data_lst передаются на обработку сообщений
    :param recv_data_lst:
    :param messages_order:
    :param clients_list:
    :return:
    """
    for client_with_message in recv_data_lst:
        try:
            message_from_client = get_message(client_with_message)
            LOGGER.info(f'Получено сообщение от {get_ip_client(client_with_message)}')
            process_client_message(message_from_client, client_with_message, messages_order)
        except json.JSONDecodeError:
            LOGGER.critical(
                f'Не удалось декодировать сообщение от клиента {get_ip_client(client_with_message)}')
            client_with_message.close()
            LOGGER.info(f'Сокет закрыт {get_ip_client(client_with_message)}')
        except NonDictInputError:
            LOGGER.critical(f'Сообщение не является словарем')
            client_with_message.close()
            LOGGER.info(f'Сокет закрыт {get_ip_client(client_with_message)}')
    return


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
    messages = {}

    while True:
        try:
            client_socket, client_address = transport.accept()  # проверка подключений
        except OSError as e:
            pass
        else:
            LOGGER.info(f'Подключение клиента {client_address[0]}:{client_address[1]}')
            clients.append(client_socket)

        # проверить наличие событий ввода-вывода без таймаута
        recv_data_lst = []
        send_data_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, _ = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # получение сообщений от клиентов и сохранение в словарь для трансляции
        if recv_data_lst:
            recv_message_from_clients(recv_data_lst, messages, clients)

        # еслиесть сообщения для отправки и  ожидающие клиенты, отправляем сообщение
        if send_data_lst and messages:
            for client_with_message in messages:
                LOGGER.debug(f'Определение сообщения для отправки от клиента {get_ip_client(client_with_message)}')
                message = messages[client_with_message]
                LOGGER.debug(f'Сообщение для отправки {message}')
                send_message_for_waiting(message, send_data_lst)
            messages.clear()
            LOGGER.debug(f'Все сообщения из очереди сообщений "messages" отправлены, очистка очереди')


if __name__ == '__main__':
    main()
