from variables import MAX_PACKAGE_LENGTH, ENCODING
from
import json

'''
Утилита приема и декодирования сообщения
принимает байты и выдает словарь, если принято, что-то другое отдает ошибку значения
:param client:
:return:
'''
def get_message(client_socket):
    encoded_response = client_socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response= encoded_response.decode(ENCODING)
        response=json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError

'''
Утилита кодирования и отправки сообщения
принимает словарь и отправляет его
:param sock:
:param message:
:return:
'''

def send_message(client_socket, message):
    if not isinstance(message, dict):
        raise TypeError
    json_message=json.dumps(message)
    encoding_message=json_message.encode(ENCODING)
    client_socket.send(encoding_message)



