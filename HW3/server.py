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


def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь ответ для клиента
    :param message:
    :return:
    """
    if isinstance(message, dict):
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


def main():
    print('запуск сервера')
    try:
        listen_port = check_port()
    except IndexError:
        sys.exit('После параметра -\'p\' необходимо указать номер порта для подключения')
    except ValueError:
        sys.exit('В качестве порта укажите значение от 1024 до 65535')

    try:
        listen_address = validation_address_ipv4(check_address())
    except IndexError:
        sys.exit('После параметра -\'a\' можно указать IP адрес клиента, остальные клиенты будут отклонены')
    except TypeError:
        sys.exit('IP адрес указан не правильно, запишите в формате 0.0.0.0')
    except ValueError:
        sys.exit('указан некорректный IP адрес')

    # готовим сокет
    transport = socket(AF_INET, SOCK_STREAM)
    transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    # слушаем порт на входящие подключения
    transport.listen(MAX_CONNECTION)
    print('сервер запущен, ожидает подклчение клиентов')

    while True:
        client_socket, client_address = transport.accept()
        print('подключение клиента')
        try:
            message_from_client = get_message(client_socket)
            response = process_client_message(message_from_client)
            send_message(client_socket, response)
            client_socket.close()
            print('Клиент подключен')
        except (ValueError, json.JSONDecodeError):
            print('Получено не корректное сообщение от клиента.')
            client_socket.close()


if __name__ == '__main__':
    main()
