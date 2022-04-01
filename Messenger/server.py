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
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTION, PRESENCE, TIME, USER, ERROR, \
    MESSAGE, MESSAGE_TEXT, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SENDER, DESTINATION, EXIT, FOR_ALL
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4, \
    get_addr_port
from errors import ReqFieldMissingError, NonDictInputError, IncorrectDataRecivedErrors
from decos import log
import logging
import logs_config.server_log_config

LOGGER = logging.getLogger('server')

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
                RESPONSE: 400,
                ERROR: 'Bad request'
                }


@log
def process_client_message(message, client_sock, messages_order, clients, clients_name):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь ответ для клиента
    :param message:
    :param client_sock:
    :param messages_order:
    :param clients:
    :param clients_name:
    :return:
    """
    LOGGER.debug(f'разбор сообщения от клиента {get_addr_port(client_sock)}')
    if isinstance(message, dict):
        #если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] != '':

            if message[USER][ACCOUNT_NAME] not in clients_name.keys():
                clients_name[message[USER][ACCOUNT_NAME]] = client_sock
                send_message(client_sock, RESPONSE_200)
                LOGGER.info(f'Код:200, сообщение PRESENSE от клиента - '
                             f'"{message[USER][ACCOUNT_NAME]}" - {get_addr_port(client_sock)}')
            else:
                response = RESPONSE_400
                response[ERROR] = f'имя клиента уже занято {message[USER][ACCOUNT_NAME]}'
                send_message(client_sock, response)
                LOGGER.error(f'Код:400, имя клиента уже занято {message[USER][ACCOUNT_NAME]}')
                clients.remove(client_sock)
                LOGGER.info(f'Сокет закрыт {get_addr_port(client_sock)}')
                client_sock.close()
                clients_name.pop(message[USER][ACCOUNT_NAME])
            return

        # если это соощение от клиента, передаем в очередь сообщений
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and SENDER in message and DESTINATION in message\
                and MESSAGE_TEXT in message:
            LOGGER.info(f'Код:200, сообщение TEXT_MESSAGE от клиента - '
                        f'"{message[SENDER]}" - {get_addr_port(client_sock)}')
            messages_order[message[DESTINATION]] = message
            return messages_order

        # если это соощение от клиента с параметром EXIT, закрываем сокет, очищаем список клиентов
        elif ACTION in message and message[ACTION] == EXIT and TIME in message \
                and SENDER in message:
            LOGGER.info(f'Код:200, cообщение ACTION:EXIT от клиента - '
                        f'"{message[SENDER]}"-{get_addr_port(clients_name[message[SENDER]])}:{message}')
            clients.remove(clients_name[message[SENDER]])
            # messages_order[FOR_ALL] = message
            LOGGER.info(f'Сокет закрыт {clients_name[message[SENDER]]}')
            clients_name[message[SENDER]].close()
            del clients_name[message[SENDER]]
            return
        else:
            LOGGER.error(f'Код:400, структура сообщения от клиента {get_addr_port(client_sock)} '
                         f'не корректна - {message}')
            send_message(client_sock, RESPONSE_400)
            return
    else:
        LOGGER.error(f'Код:400, от клиента {get_addr_port(client_sock)} '
                     f'не корректный тип сообщения - {message}')
        send_message(client_sock, RESPONSE_400)
        return


@log
def new_listen_socket(address, port):
    """
    Подготовка сокета на сервере
    :param address:
    :param port:
    :return: sock
    """
    # готовим сокет
    LOGGER.debug(f'Запуск сокета')
    sock = socket(AF_INET, SOCK_STREAM)
    LOGGER.debug(f'Установка параметров сокета')
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((address, port))

    # слушаем порт на входящие подключения
    sock.listen(MAX_CONNECTION)
    LOGGER.info(f'Сервер {address}:{port} запущен, ожидает подклчение клиентов')
    sock.settimeout(0.2)
    return sock


@log
def send_message_for_waiting(dest_name, messages, clients_name, clients):
    """
    Отправка сообщения всем клиентам
    :param dest_name:
    :param messages:
    :param clients_name:
    :param clients:
    :return:
    """
    try:
        print('отправка', dest_name, messages[dest_name])
        send_message(clients_name[dest_name], messages[dest_name])
        LOGGER.info(f'Cообщение для {dest_name}-{get_addr_port(clients_name[dest_name])} отправлено')
    except Exception as e:
        LOGGER.error(f'{e}'
                     f'Клиент  {clients_name[dest_name]} отключился от сервера')
        clients.remove(clients_name[dest_name])
        LOGGER.debug(f'Клиент {dest_name} удален из списка получателей сообщений')
        LOGGER.info(f'Сокет клиента {dest_name} - {get_addr_port(clients_name[dest_name])} закрыт')
        clients_name[dest_name].close()
        clients_name.pop(dest_name)
    return


@log
def recv_message_from_clients(recv_data_lst, messages_order, clients, clients_name):
    """
    Каждое сообщения из recv_data_lst передаются на обработку сообщений
    :param recv_data_lst:
    :param messages_order:
    :param clients:
    :param clients_name:
    :return:
    """
    for client_with_message in recv_data_lst:
        try:
            message_from_client = get_message(client_with_message)
            LOGGER.debug(f'Получено сообщение от {get_addr_port(client_with_message)}')
            process_client_message(message_from_client, client_with_message, messages_order, clients, clients_name)
        except json.JSONDecodeError:
            LOGGER.critical(
                f'Не удалось декодировать сообщение от клиента {get_addr_port(client_with_message)}')
            clients.remove(client_with_message)
            LOGGER.error(f'Сокет закрыт {get_addr_port(client_with_message)}')
            client_with_message.close()
        except NonDictInputError:
            LOGGER.critical(f'Сообщение не является словарем')
            clients.remove(client_with_message)
            LOGGER.error(f'Сокет закрыт {get_addr_port(client_with_message)}')
            client_with_message.close()
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            LOGGER.critical(f'Потеряно соединение с клиентом {get_addr_port(client_with_message)}')
            clients.remove(client_with_message)
            LOGGER.error(f'Сокет закрыт {get_addr_port(client_with_message)}')
            client_with_message.close()
    return


@log
def arg_parser():
    """
    Создаем парсер аргументов командной строки и читаем параметры
    :return listen_address, listen_port:
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('-p', '--port', default=DEFAULT_PORT, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        arg_listen_address = namespace.addr
        arg_listen_port = int(namespace.port)

    except Exception as e:
        print('Введены некорректные параметры запуска сервера')
        LOGGER.error(f'{e} Введены некорректные параметры запуска сервера')
        sys.exit(1)

    # проверка адреса сервера
    try:
        listen_address = validation_address_ipv4(arg_listen_address)
        LOGGER.debug(f'Адрес сервера определен {listen_address}')
    except IndexError:
        LOGGER.error('Не указан IP сервера, после параметра -a')
        sys.exit(1)
    except TypeError:
        LOGGER.error(f'IP адрес указан не правильно - {arg_listen_address}')
        sys.exit(1)
    except ValueError:
        LOGGER.error(f'Указан некорректный IP адрес сервера - {arg_listen_address}')
        sys.exit(1)

    # проверка номера порта
    try:
        listen_port = check_port(arg_listen_port)
        LOGGER.debug(f'Порт сервера определен {listen_port}')
    except IndexError:
        LOGGER.error('Не указан порт сервера, после параметра -p')
        sys.exit(1)
    except ValueError:
        LOGGER.error(f'Указан не корректный порт {arg_listen_port}')
        sys.exit(1)

    LOGGER.info(f'Запущен сервер с параметрами:'
                f' адрес сервера: {listen_address}, порт: {listen_port}')
    return listen_address, listen_port


def main():
    LOGGER.info(f'Запуск сервера')
    listen_address, listen_port = arg_parser()

    transport = new_listen_socket(listen_address, listen_port)
    print(f'Cервер запущен - {listen_address}:{listen_port}')

    # список клиентов(сокетов), словарь сообщений для отправки
    clients = []
    messages = dict()  # {client_name: client_socket}

    #словарь, содержащий имена пользователей и соответствующие им сокеты
    clients_name = dict()  # {client_name: client_socket}

    while True:
        try:
            client_socket, client_address = transport.accept()  # проверка подключений
        except OSError:
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
        except (OSError, ValueError):
            pass

        # получение сообщений от клиентов и сохранение в словарь для трансляции
        if recv_data_lst:
            recv_message_from_clients(recv_data_lst, messages, clients, clients_name)

        # еслиесть сообщения для отправки и  ожидающие клиенты, отправляем сообщение
        if send_data_lst and messages:
            for destination in messages.keys():
                LOGGER.debug(f'Выбраны получатели {destination}')
                if destination == FOR_ALL:
                    LOGGER.debug(f'Выбраны получатели: {clients_name.keys()}')
                    for d_name in clients_name.keys():
                        # time.sleep(0.5)
                        LOGGER.debug(f'Получатель: {d_name}, {messages[destination]}')
                        send_message_for_waiting(d_name, messages, clients_name, clients)
                elif destination != FOR_ALL:
                    LOGGER.debug(f'Получатель: {destination}, {messages[destination]}')
                    send_message_for_waiting(destination, messages, clients_name, clients)
            messages.clear()
            LOGGER.debug(f'Все сообщения из очереди сообщений "messages" отправлены, очистка очереди')


if __name__ == '__main__':
    main()
