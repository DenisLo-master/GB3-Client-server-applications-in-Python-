import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.utilites import get_message, send_message
from common.variables import ACTION, ACCOUN_NAME, PRESENSE, TIME, USER, DEFAULT_PORT, DEFAULT_IP_ADDRESS

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
    return server_address, server_port

# готовим сокет
transport = socket(AF_INET, SOCK_STREAM)
transport.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# подключение к серверу
transport.connect((server_address, connect_port))


# PRESENSE сообщение для сервера в формате JIM
def create_presense(accaunt_name='Guest'):
    message = {
        ACTION: PRESENSE,
        TIME: time.time(),
        USER: {
            ACCOUN_NAME: accaunt_name
        },
    }
    return message


send_message(transport, create_presense())
message_from_server = get_message(transport)
print(message_from_server)
