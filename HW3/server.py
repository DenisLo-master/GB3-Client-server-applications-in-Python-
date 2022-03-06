# клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата. Клиент и сервер должны быть
# реализованы в виде отдельных скриптов, содержащих соответствующие функции. Функции клиента: сформировать
# presence-сообщение; отправить сообщение серверу; получить ответ сервера; разобрать сообщение сервера; параметры
# командной строки скрипта client.py <addr> [<port>]: addr — ip-адрес сервера; (по умолчанию 127.0.0.1); port —
# tcp-порт на сервере, (по умолчанию 7777). Функции сервера: принимает сообщение клиента; формирует ответ клиенту;
# отправляет ответ клиенту; имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию
# использует 7777); -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).

import sys
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.variables import ACTION, ACCOUN_NAME, RESPONSE, MAX_CONNECTION, PRESENSE, TIME, USER, ERROR, DEFAULT_PORT, \
    RESPONDEFAULT_IP_ADDRESS
from common.utilites import get_message, send_message
import json


def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь ответ для клиента
    :param message:
    :return:
    """
    if ACTION in message and message[ACTION] == PRESENSE and TIME in message \
            and USER in message and message[USER][ACCOUN_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad request'
    }


try:
    if '-p' in sys.argv:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1])
    else:
        listen_port = DEFAULT_PORT
    if listen_port < 1024 or listen_port > 65535:
        raise ValueError
except IndexError:
    print('После параметра -\'p\' необходимо указать номер порта')
    sys.exit(1)
except ValueError:
    print('В качестве порта может быть указано значение от 1024 до 65535')
    sys.exit(1)

try:
    if '-a' in sys.argv:
        listen_address = int(sys.argv[sys.argv.index('-a') + 1])
    else:
        listen_address = ''

except IndexError:
    print('После параметра -\'a\' необходимо указать адрес клиента, который будет слушать сервер')
    sys.exit(1)

# готовим сокет
transport = socket(AF_INET, SOCK_STREAM)
transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
transport.bind((listen_address, listen_port))

# слушаем порт на входящие подключения
transport.listen(MAX_CONNECTION)

while True:
    client_socket, client_address = transport.accept()
    try:
        message_from_client = get_message(client_socket)
        print(message_from_client)
        response = process_client_message(message_from_client)
        send_message(client_socket, response)
        client_socket.close()
    except (ValueError, json.JSONDecodeError):
        print('Получено не корректное сообщение от клиента.')
        client_socket.close()
