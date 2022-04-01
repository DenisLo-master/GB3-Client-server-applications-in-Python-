""" Константы """

# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTION = 5
# Максимальная длина сообщений в байтах
MAX_PACKAGE_LENGTH = 4096
# Кодировка проекта
ENCODING = 'utf-8'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'destination'
MESSAGE_TEXT = 'message_text'



# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
MESSAGE = 'message'
EXIT = 'exit'
ERROR = 'error'
CLIENT_STATUS = 'client_status'
FOR_ALL = 'for_all'


# Уровень логгирования
LOGGING_REGISTRAR_LEVEL = 'DEBUG'
FILE_LOGGING_LEVEL = 'INFO'
STREAM_LOGGING_LEVEL = 'ERROR'
