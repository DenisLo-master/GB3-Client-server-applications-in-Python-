import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message
from common.variables import ACTION, ACCOUN_NAME, PRESENSE, RESPONSE, TIME, USER, ERROR, DEFAULT_PORT, \
    DEFAULT_IP_ADDRESS


def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутсвии клиента
    : param account_name:
    :return:
    """
    message = {
        ACTION: PRESENSE,
        TIME: time.time(),
        USER: {
            ACCOUN_NAME: account_name
        },
    }
    return message


def process_answer(message):
    """
    Функция разирает ответ сервера
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


def main():
    try:
        if '-p' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            server_port = DEFAULT_PORT
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта')
        sys.exit(1)
    except ValueError:
        print('В качестве порта может быть указано значение от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            server_address = int(sys.argv[sys.argv.index('-a') + 1])
        else:
            server_address = DEFAULT_IP_ADDRESS

    except IndexError:
        print('После параметра -\'a\' необходимо указать адрес клиента, который будет слушать сервер')
        sys.exit(1)

    # готовим сокет
    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # подключение к серверу
    transport.connect((server_address, server_port))

    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = process_answer(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение от сервера')


if __name__ == '__main__':
    main()
