from common.variables import MAX_PACKAGE_LENGTH, ENCODING, DEFAULT_IP_ADDRESS
import json
import sys
from decos import log


@log
def get_message(client_socket):
    """
    Утилита приема и декодирования сообщения
    принимает байты и выдает словарь, если принято,
    что-то другое отдает ошибку значения
    :param client_socket:
    :return:
    """
    encoded_response = client_socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise TypeError
    raise TypeError


@log
def send_message(client_socket, message):
    """
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param client_socket:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise TypeError
    json_message = json.dumps(message)
    encoding_message = json_message.encode(ENCODING)
    client_socket.send(encoding_message)


@log
def check_port(port):
    """
    Утилита для проверки введенного порта через командную строку, либо присвоение значение по умолчанию
    :return:
    """
    if port < 1024 or port > 65535:
        raise ValueError
    return port


@log
def check_address():
    """
    Утилита для проверки наличия введенного ip адреса через командную строку, либо присвоение значения по умолчанию
    :return:
    """
    if '-a' in sys.argv:
        argv_address = sys.argv[sys.argv.index('-a') + 1]
    else:
        argv_address = DEFAULT_IP_ADDRESS
    return argv_address


@log
def validation_address_ipv4(address):
    """
    Утилита для проверки валидности полученного ip адреса
    :param address:
    :return:
    """

    if address is not None:
        if len(address.split('.')) == 4:
            for item in address.split('.'):
                if int(item) < 0 or int(item) > 255:
                    raise ValueError
            return address
        else:
            raise TypeError
    else:
        raise IndexError


@log
def get_addr_port(sock):
    """
    Получение адреса и порт клиента из сокета
    :param sock:
    :return: addr
    """
    addr = f'{sock.getsockname()[0]}:{sock.getsockname()[1]}'
    return addr