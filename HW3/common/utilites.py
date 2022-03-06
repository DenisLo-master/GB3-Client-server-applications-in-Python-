import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING


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
        raise ValueError
    raise ValueError


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
