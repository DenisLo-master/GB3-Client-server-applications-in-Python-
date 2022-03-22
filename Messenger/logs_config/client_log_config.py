"""Конфигурация логгера на клиенте"""

import logging
import os.path
import sys
from logging import handlers
sys.path.append('../')
from common.variables import LOGGING_REGISTRAR_LEVEL, STREAM_LOGGING_LEVEL, FILE_LOGGING_LEVEL


# формировщик логов (dormatter)
SERVER_FORMATTER = logging.Formatter('%(asctime)-26s %(levelname)-10s %(filename)-23s %(message)s')

# подготовка файла для сбора логов

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client_log')
if not os.path.exists(PATH):
    os.mkdir(PATH)
PATH = os.path.join(PATH, 'client.log')


#потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(STREAM_LOGGING_LEVEL)

LOG_FILE = logging.handlers.RotatingFileHandler(PATH, encoding='utf-8', maxBytes=100000000)
LOG_FILE.setFormatter(SERVER_FORMATTER)
LOG_FILE.setLevel(FILE_LOGGING_LEVEL)

#регистратор

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_REGISTRAR_LEVEL)

#отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.warning('Предупреждения')
    LOGGER.info('Информационное сообщение')