import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message, check_port, check_address, validation_address_ipv4
from common.variables import ACTION, ACCOUNT_NAME, PRESENCE, RESPONSE, TIME, USER, ERROR


def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутсвии клиента
    : param account_name:
    :return:
    """
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
    }
    return message


def process_answer(message):
    """
    Функция разирает ответ сервера
    :param message:
    :return:
    """
    if isinstance(message, dict):
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200: OK'
            elif message[RESPONSE] == 400:
                return f'400: {message[ERROR]}'
            else:
                raise IndexError
        raise ValueError
    raise TypeError


def main():
    try:
        server_port = check_port()
    except IndexError:
        sys.exit('После параметра -\'p\' необходимо указать номер порта')
    except ValueError:
        sys.exit('В качестве порта укажите значение от 1024 до 65535')

    try:
        server_address = validation_address_ipv4(check_address())
    except IndexError:
        sys.exit('После параметра -\'a\' необходимо указать адрес сервера для подключения')
    except TypeError:
        sys.exit('IP адрес указан не правильно, запишите в формате 0.0.0.0')
    except ValueError:
        sys.exit('указан некорректный IP адрес')

    # готовим сокет
    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # подключение к серверу
    print(f'Подключение к серверу: {server_address}:{server_port}')
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
